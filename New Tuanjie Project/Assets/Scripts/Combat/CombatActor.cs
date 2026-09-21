using UnityEngine;

/// <summary>行为脑：玩家=输入缓冲，敌人=AI。每固定帧先于状态执行。</summary>
public abstract class Brain
{
    public CombatActor actor;
    public virtual void Think() { }
}

/// <summary>
/// 战斗角色基类：资源（气血/内力/架势）、状态机、受击结算、灰盒表现。
/// 所有战斗逻辑按 60FPS 固定帧推进；freezeFrames 实现打击停顿。
/// </summary>
public class CombatActor : MonoBehaviour
{
    [Header("身份")]
    public string displayName = "无名";
    public bool isPlayer;

    [Header("资源")]
    public float maxHP = 100f;
    public float hp;
    public float maxChi = 100f;
    public float chi;
    public float maxPoise;   // 0 = 无架势条（玩家）
    public float poise;

    [Header("机动")]
    public float runSpeed = 5.5f;
    public float jumpVel = 13.5f;
    public float gravity = 30f;

    [HideInInspector] public int facing = 1;
    [HideInInspector] public KinematicBody2D body;
    [HideInInspector] public Brain brain;
    [HideInInspector] public Intents inp;
    [HideInInspector] public ActorState state;
    [HideInInspector] public int freezeFrames;
    [HideInInspector] public int iframesUntil = -1; // 全局帧号，含
    [HideInInspector] public int lastHitTakenFrame = -9999;
    [HideInInspector] public bool dead;
    [HideInInspector] public bool airDodgeUsed;
    [HideInInspector] public int airLightStep; // 空中连段计数

    // 青锋·剑意（仅玩家使用）
    [HideInInspector] public int intent;          // 0..5
    [HideInInspector] public bool bloomArmed;     // 剑意绽放已武装
    [HideInInspector] public int bloomUntilFrame; // 绽放有效期
    [HideInInspector] public int lastIntentGainFrame = -9999;

    // 表现
    SpriteRenderer bodySr;
    SpriteRenderer trimSr;
    SpriteRenderer weaponSr;
    Transform weaponTr;
    Color baseColor;
    Color trimColor;
    float weaponAngle, weaponLen, weaponAlpha = 0f;
    Animator playerAnim;
    SpriteRenderer playerSr;

    public Vector2 FeetPos { get { return body.pos; } }
    public bool Invulnerable
    {
        get
        {
            if (CombatDirector.Frame <= iframesUntil) return true;
            DodgeState d = state as DodgeState;
            if (d != null && d.IFramesActive) return true;
            return false;
        }
    }

    public void Init(string name, bool player, Vector2 spawn, Color bodyColor, Color trim)
    {
        displayName = name;
        isPlayer = player;
        body = new KinematicBody2D();
        body.pos = spawn;
        hp = maxHP;
        chi = isPlayer ? 60f : 0f;
        poise = maxPoise;

        baseColor = bodyColor;
        if (isPlayer && SetupPlayerSprite())
        {
            ChangeState(new GroundedState(this));
            return;
        }

        GameObject bodyGo = SpriteFactory.CreateBox(transform, "Body", new Vector2(0.7f, 1.4f), bodyColor, 5);
        bodyGo.transform.localPosition = new Vector3(0f, 0.7f, 0f);
        bodySr = bodyGo.GetComponent<SpriteRenderer>();

        GameObject trimGo = SpriteFactory.CreateBox(transform, "Trim", new Vector2(0.72f, 0.16f), trim, 6);
        trimGo.transform.localPosition = new Vector3(0f, 0.86f, 0f);
        trimSr = trimGo.GetComponent<SpriteRenderer>();
        trimColor = trim;

        GameObject nose = SpriteFactory.CreateBox(transform, "Nose", new Vector2(0.12f, 0.12f), trim, 6);
        nose.transform.localPosition = new Vector3(0.32f, 1.15f, 0f);

        GameObject weaponGo = SpriteFactory.CreateBox(transform, "Weapon", new Vector2(1f, 0.09f), new Color(0.85f, 0.95f, 1f), 7);
        weaponTr = weaponGo.transform;
        weaponSr = weaponGo.GetComponent<SpriteRenderer>();
        weaponTr.localPosition = new Vector3(0.4f, 0.9f, 0f);
        weaponSr.enabled = false;

        ChangeState(new GroundedState(this));
    }

    void FixedUpdate()
    {
        if (CombatDirector.Instance == null) return;
        if (freezeFrames > 0) { freezeFrames--; return; }
        if (dead)
        {
            state.Tick();
            if (!body.grounded) body.vel.y = Mathf.Max(body.vel.y - gravity * Time.fixedDeltaTime, -22f);
            body.Simulate(Time.fixedDeltaTime);
            return;
        }

        if (brain != null) brain.Think();
        state.Tick();

        // 重力与位移（攻击/闪避状态会直接改 vel）
        if (!body.grounded) body.vel.y = Mathf.Max(body.vel.y - gravity * Time.fixedDeltaTime, -22f);
        body.Simulate(Time.fixedDeltaTime);

        if (body.grounded)
        {
            airDodgeUsed = false;
            airLightStep = 0;
        }

        // 架势回复：3秒未受击后缓慢回
        if (maxPoise > 0f && poise < maxPoise && CombatDirector.Frame - lastHitTakenFrame > 180)
            poise = Mathf.Min(maxPoise, poise + maxPoise / 300f);

        // 剑意衰减：脱战3秒后每秒-1
        if (isPlayer && intent > 0 && CombatDirector.Frame - lastIntentGainFrame > 180)
        {
            if (CombatDirector.Frame % 60 == 0) intent--;
        }
        if (bloomArmed && CombatDirector.Frame > bloomUntilFrame) bloomArmed = false;

        inp.ClearOneShots();
    }

    bool SetupPlayerSprite()
    {
        RuntimeAnimatorController ctrl = PlayerVisualLoader.LoadController();
        if (ctrl == null) return false;

        playerSr = gameObject.AddComponent<SpriteRenderer>();
        playerSr.sortingOrder = 8;
        playerAnim = gameObject.AddComponent<Animator>();
        playerAnim.runtimeAnimatorController = ctrl;
        if (GetComponent<CharacterFootskateFix>() == null)
            gameObject.AddComponent<CharacterFootskateFix>();
        return true;
    }

    void Update()
    {
        transform.position = new Vector3(body.pos.x, body.pos.y, 0f);
        if (playerAnim != null)
        {
            float speed = (state is GroundedState) ? Mathf.Abs(inp.moveX) : 0f;
            playerAnim.SetFloat("Speed", speed);
            if (playerSr != null) playerSr.flipX = facing < 0;
        }
        else
        {
            Vector3 s = transform.localScale;
            s.x = Mathf.Abs(s.x) * facing;
            transform.localScale = s;
        }
        UpdateVisual();
    }

    public void ChangeState(ActorState next)
    {
        if (state != null) state.Exit();
        state = next;
        state.Enter();
    }

    /// <summary>状态消费了一个一次性意图：通知脑移除对应缓冲，防止重复触发。</summary>
    public void Consume(string action)
    {
        PlayerBrain pb = brain as PlayerBrain;
        if (pb != null) pb.ConsumeAction(action);
    }

    // ---------------- 受击 ----------------

    public void ApplyHit(HitInfo h, CombatActor attacker)
    {
        if (dead) return;
        if (Invulnerable) return;

        // 格挡/弹反判定
        BlockState bs = state as BlockState;
        if (bs != null && !h.unblockable)
        {
            int dx = attacker != null ? (int)Mathf.Sign(attacker.body.pos.x - body.pos.x) : facing;
            if (dx == facing || attacker == null)
            {
                bs.ResolveHit(h, attacker);
                return;
            }
        }

        lastHitTakenFrame = CombatDirector.Frame;

        // 霸体：只掉血不掉状态
        AttackState atk = state as AttackState;
        bool armored = atk != null && atk.InArmorFrames;

        hp -= h.damage;
        if (maxPoise > 0f) poise -= h.poise;

        // 打击停顿双方
        freezeFrames = Mathf.Max(freezeFrames, h.hitstop);
        if (attacker != null) attacker.freezeFrames = Mathf.Max(attacker.freezeFrames, h.hitstop);

        if (attacker != null) attacker.OnHitLanded(this, h);

        Flash(Color.red);

        if (hp <= 0f)
        {
            hp = 0f;
            Die();
            return;
        }

        if (armored) return; // 霸体不中断

        // 架势破：长硬直
        if (maxPoise > 0f && poise <= 0f)
        {
            poise = maxPoise;
            CombatDirector.Msg("破防!", body.pos + new Vector2(0, 1.8f), new Color(1f, 0.8f, 0.2f), 60);
            CombatDirector.Shake(0.25f, 12);
            ChangeState(new HitstunState(this, 60, true));
            return;
        }

        ChangeState(new HitstunState(this, h.hitstun, false));
    }

    /// <summary>弹反强制中断（无视霸体），并附架势伤害。</summary>
    public void ForceInterrupt(int stunFrames, float poiseDmg)
    {
        if (dead) return;
        if (maxPoise > 0f)
        {
            poise -= poiseDmg;
            if (poise <= 0f)
            {
                poise = maxPoise;
                CombatDirector.Msg("破防!", body.pos + new Vector2(0, 1.8f), new Color(1f, 0.8f, 0.2f), 60);
                ChangeState(new HitstunState(this, 60, true));
                return;
            }
        }
        ChangeState(new HitstunState(this, stunFrames, false));
    }

    /// <summary>命中对手后的回收：内力、剑意、击杀。</summary>
    public void OnHitLanded(CombatActor victim, HitInfo h)
    {
        if (!isPlayer) return;
        chi = Mathf.Min(maxChi, chi + 4f);
        GainIntent(1);
        if (victim.dead || victim.hp <= 0f) chi = Mathf.Min(maxChi, chi + 15f);
    }

    public void GainIntent(int n)
    {
        if (!isPlayer) return;
        lastIntentGainFrame = CombatDirector.Frame;
        intent = Mathf.Min(5, intent + n);
        if (intent >= 5) ArmBloom();
    }

    public void ArmBloom()
    {
        bloomArmed = true;
        bloomUntilFrame = CombatDirector.Frame + 90;
        CombatDirector.Msg("剑意绽放!", body.pos + new Vector2(0, 1.9f), new Color(0.6f, 0.95f, 1f), 50);
    }

    public void Die()
    {
        dead = true;
        ChangeState(new DeadState(this));
        if (isPlayer) CombatDirector.OnPlayerDeath();
    }

    // ---------------- 表现 ----------------

    void Flash(Color c)
    {
        if (bodySr != null) bodySr.color = Color.Lerp(baseColor, c, 0.7f);
    }

    void UpdateVisual()
    {
        if (bodySr == null) return;
        Color target = baseColor;
        float targetWeaponAlpha = 0f;
        float targetWeaponAngle = 0f;
        float targetWeaponLen = 1f;

        if (dead)
        {
            target = Color.Lerp(baseColor, Color.black, 0.6f);
        }
        else
        {
            AttackState atk = state as AttackState;
            if (atk != null)
            {
                MoveData mv = atk.Move;
                if (atk.InStartup)
                {
                    // 前摇：敌人红闪（霸体橙红），玩家剑光微亮
                    if (!isPlayer)
                    {
                        float t = atk.StartupProgress;
                        Color tele = mv.armorFrom > 0 ? new Color(1f, 0.45f, 0.1f) : Color.red;
                        target = Color.Lerp(baseColor, tele, 0.35f + 0.55f * t);
                    }
                    targetWeaponAlpha = 0.45f;
                    targetWeaponAngle = -55f;
                    targetWeaponLen = Mathf.Max(0.6f, mv.reach * 0.8f);
                }
                else if (atk.InActive)
                {
                    targetWeaponAlpha = 1f;
                    targetWeaponAngle = 0f;
                    targetWeaponLen = Mathf.Max(0.8f, mv.boxW * 0.75f);
                    if (isPlayer && bloomArmed) target = Color.Lerp(baseColor, new Color(1f, 0.9f, 0.4f), 0.5f);
                }
                else
                {
                    targetWeaponAlpha = 0.25f;
                    targetWeaponAngle = 25f;
                    targetWeaponLen = Mathf.Max(0.5f, mv.reach * 0.6f);
                }
            }
            else if (state is BlockState)
            {
                targetWeaponAlpha = 0.9f;
                targetWeaponAngle = 80f;
                targetWeaponLen = 0.8f;
                target = Color.Lerp(baseColor, Color.cyan, 0.15f);
            }
            else if (state is DodgeState)
            {
                target = Color.Lerp(baseColor, Color.white, 0.35f);
            }
            else if (state is HitstunState)
            {
                target = Color.Lerp(baseColor, Color.red, 0.45f);
            }
        }

        bodySr.color = Color.Lerp(bodySr.color, target, 0.35f);
        if (trimSr != null) trimSr.color = trimColor;

        weaponAlpha = Mathf.Lerp(weaponAlpha, targetWeaponAlpha, 0.4f);
        weaponAngle = Mathf.Lerp(weaponAngle, targetWeaponAngle, 0.45f);
        weaponLen = Mathf.Lerp(weaponLen, targetWeaponLen, 0.4f);
        if (weaponSr != null)
        {
            weaponSr.enabled = weaponAlpha > 0.05f;
            Color wc = weaponSr.color; wc.a = weaponAlpha; weaponSr.color = wc;
            weaponTr.localRotation = Quaternion.Euler(0f, 0f, weaponAngle);
            weaponTr.localScale = new Vector3(weaponLen, 1f, 1f);
            weaponTr.localPosition = new Vector3(0.25f + weaponLen * 0.4f, 0.9f, 0f);
        }
    }
}
