using System.Collections;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// 角色动画预览与操控器（SpritePreview 场景）：
/// 支持 WASD 行走/奔跑/跳跃/闪避、J/K 攻击连段、F/G/T 格挡与弹反，以及 Q/U 破空刺技能。
/// 提供屏幕快捷按键 UI 面板，支持鼠标直觉点击或键盘热键即时触发任意动作。
/// </summary>
[RequireComponent(typeof(Animator))]
[RequireComponent(typeof(SpriteRenderer))]
public class PlayerSpriteLocomotion : MonoBehaviour
{
    const float WalkThreshold = 0.1f;
    const float WalkAnimSpeed = 0.4f;
    const float DodgeDuration = 0.60f;
    const float JumpVelocity = 8.5f;
    const float Gravity = 24.0f;
    const float BlockDuration = 0.68f;
    const float ParryWindow = 0.18f;

    public Animator animator;
    public SpriteRenderer spriteRenderer;
    CombatActor combat;

    float dodgeTimer = 0f;
    float dodgeDir = 1f;
    float blockTimer = 0f;

    public bool IsBlocking => blockTimer > 0f;
    public bool IsParryWindow => blockTimer > 0f && (BlockDuration - blockTimer) <= ParryWindow;

    float velY = 0f;
    float groundY = 0f;
    bool isGrounded = true;

    int attackStep = 0;
    float attackTimer = 0f;
    float comboWindow = 0f;
    float lungeTimer = 0f;
    float lungeSpeed = 0f;

    // 破空刺/回风舞/一剑霜寒 技能帧与状态
    bool isSkillPlaying = false;
    [SerializeField] public Sprite[] pokongciSprites;
    [SerializeField] public Sprite[] huifengwuSprites;
    [SerializeField] public Sprite[] yijianshuanghanSprites;
    string currentActionName = "待机 (Idle)";

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
    static void AutoAttachInPreview()
    {
        GameObject go = GameObject.Find("QingfengIdle");
        if (go == null) return;
        if (go.GetComponent<PlayerSpriteLocomotion>() == null)
            go.AddComponent<PlayerSpriteLocomotion>();
        if (go.GetComponent<CharacterFootskateFix>() == null)
            go.AddComponent<CharacterFootskateFix>();
        FootskateDebugGrid.SpawnIfMissing();
    }

    void Awake()
    {
        animator = GetComponent<Animator>();
        spriteRenderer = GetComponent<SpriteRenderer>();
        combat = GetComponent<CombatActor>();
        groundY = transform.position.y;
        LoadPokongciSprites();
        LoadHuifengwuSprites();
        LoadYijianshuanghanSprites();
    }

    public void LoadYijianshuanghanSprites()
    {
#if UNITY_EDITOR
        List<Sprite> list = new List<Sprite>();
        for (int i = 1; i <= 8; i++)
        {
            string p = $"Assets/Sprites/Player/Skills/Yijianshuanghan/yijianshuanghan-{i}.png";
            Sprite sp = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>(p);
            if (sp != null) list.Add(sp);
        }
        if (list.Count >= 8)
        {
            yijianshuanghanSprites = list.ToArray();
            return;
        }
#endif
        LoadYijianshuanghanSpritesFromDisk();
    }

    void LoadYijianshuanghanSpritesFromDisk()
    {
        string dir = System.IO.Path.Combine(Application.dataPath, "Sprites/Player/Skills/Yijianshuanghan");
        List<Sprite> list = new List<Sprite>();
        for (int i = 1; i <= 8; i++)
        {
            string filePath = System.IO.Path.Combine(dir, $"yijianshuanghan-{i}.png");
            if (System.IO.File.Exists(filePath))
            {
                byte[] bytes = System.IO.File.ReadAllBytes(filePath);
                Texture2D tex = new Texture2D(680, 480, TextureFormat.RGBA32, false);
                tex.filterMode = FilterMode.Bilinear;
                if (tex.LoadImage(bytes))
                {
                    Sprite sp = Sprite.Create(tex, new Rect(0, 0, tex.width, tex.height), new Vector2(0.5f, 0.09f), 214f);
                    list.Add(sp);
                }
            }
        }
        if (list.Count >= 8)
        {
            yijianshuanghanSprites = list.ToArray();
            Debug.Log($"[PlayerSpriteLocomotion] Successfully loaded {yijianshuanghanSprites.Length} Yijianshuanghan sprites directly from disk!");
        }
        else
        {
            Debug.LogWarning($"[PlayerSpriteLocomotion] Failed to load 8 Yijianshuanghan sprites from disk (loaded {list.Count}) at {dir}");
        }
    }

    void LoadPokongciSprites()
    {
#if UNITY_EDITOR
        List<Sprite> list = new List<Sprite>();
        for (int i = 1; i <= 7; i++)
        {
            string p = $"Assets/Sprites/Player/Skills/Pokongci/pokongci-{i}.png";
            Sprite sp = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>(p);
            if (sp != null) list.Add(sp);
        }
        if (list.Count > 0)
        {
            pokongciSprites = list.ToArray();
        }
#endif
    }

    public void LoadHuifengwuSprites()
    {
#if UNITY_EDITOR
        List<Sprite> list = new List<Sprite>();
        for (int i = 1; i <= 8; i++)
        {
            string p = $"Assets/Sprites/Player/Skills/Huifengwu/huifengwu-{i}.png";
            Sprite sp = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>(p);
            if (sp != null) list.Add(sp);
        }
        if (list.Count >= 8)
        {
            huifengwuSprites = list.ToArray();
            return;
        }
#endif
        LoadHuifengwuSpritesFromDisk();
    }

    void LoadHuifengwuSpritesFromDisk()
    {
        string dir = System.IO.Path.Combine(Application.dataPath, "Sprites/Player/Skills/Huifengwu");
        List<Sprite> list = new List<Sprite>();
        for (int i = 1; i <= 8; i++)
        {
            string filePath = System.IO.Path.Combine(dir, $"huifengwu-{i}.png");
            if (System.IO.File.Exists(filePath))
            {
                byte[] bytes = System.IO.File.ReadAllBytes(filePath);
                Texture2D tex = new Texture2D(680, 480, TextureFormat.RGBA32, false);
                tex.filterMode = FilterMode.Bilinear;
                if (tex.LoadImage(bytes))
                {
                    Sprite sp = Sprite.Create(tex, new Rect(0, 0, tex.width, tex.height), new Vector2(0.5f, 0.09f), 214f);
                    list.Add(sp);
                }
            }
        }
        if (list.Count >= 8)
        {
            huifengwuSprites = list.ToArray();
            Debug.Log($"[PlayerSpriteLocomotion] Successfully loaded {huifengwuSprites.Length} Huifengwu sprites directly from disk!");
        }
        else
        {
            Debug.LogWarning($"[PlayerSpriteLocomotion] Failed to load 8 Huifengwu sprites from disk (loaded {list.Count}) at {dir}");
        }
    }

    void Update()
    {
        // 战斗场景若由 CombatActor/PlayerBrain 全权接管，则预览脚本自动让渡
        if (combat != null) return;

        if (animator == null) animator = GetComponent<Animator>();
        if (spriteRenderer == null) spriteRenderer = GetComponent<SpriteRenderer>();

        // 技能播放期间独占位移与帧控制
        if (isSkillPlaying)
        {
            return;
        }

        // 空中重力与落地解算
        if (!isGrounded)
        {
            velY -= Gravity * Time.deltaTime;
            Vector3 p = transform.position;
            p.y += velY * Time.deltaTime;
            if (p.y <= groundY)
            {
                p.y = groundY;
                velY = 0f;
                isGrounded = true;
                if (animator != null) animator.SetBool("IsGrounded", true);
            }
            transform.position = p;
        }

        // 闪避状态更新
        if (dodgeTimer > 0f)
        {
            dodgeTimer -= Time.deltaTime;
            currentActionName = "闪避 (Dodge)";
            float dt = Mathf.Min(Time.deltaTime, 0.20f);
            Vector3 p = transform.position;
            p.x += dodgeDir * (0.45f / 0.20f) * dt;
            transform.position = p;
            return;
        }

        // 格挡架势更新
        if (blockTimer > 0f)
        {
            blockTimer -= Time.deltaTime;
            currentActionName = "格挡架势 (Block)";

            if (Input.GetKeyDown(KeyCode.Space))
            {
                blockTimer = 0f;
                StartDodge();
                return;
            }

            if (Input.GetKeyDown(KeyCode.J) || Input.GetMouseButtonDown(0))
            {
                blockTimer = 0f;
                PerformNextAttack();
                return;
            }

            if (Input.GetKeyDown(KeyCode.K) || Input.GetMouseButtonDown(1))
            {
                blockTimer = 0f;
                PerformHeavyThrust();
                return;
            }

            if (Input.GetKeyDown(KeyCode.G))
            {
                TriggerBlockHit();
                return;
            }

            if (Input.GetKeyDown(KeyCode.T))
            {
                TriggerParrySuccess();
                return;
            }

            if (Input.GetKey(KeyCode.F) && blockTimer < 0.25f)
            {
                blockTimer = 0.25f;
            }
            return;
        }

        // 连击输入窗口衰减
        if (comboWindow > 0f)
        {
            comboWindow -= Time.deltaTime;
            if (comboWindow <= 0f) attackStep = 0;
        }

        // 攻击硬直与微位移
        if (attackTimer > 0f)
        {
            attackTimer -= Time.deltaTime;
            if (lungeTimer > 0f)
            {
                float dt = Mathf.Min(Time.deltaTime, lungeTimer);
                lungeTimer -= dt;
                float faceDir = spriteRenderer.flipX ? -1f : 1f;
                Vector3 p = transform.position;
                p.x += faceDir * lungeSpeed * dt;
                transform.position = p;
            }

            // 轻攻击允许闪避取消
            if (Input.GetKeyDown(KeyCode.Space) && attackStep < 4)
            {
                attackTimer = 0f;
                attackStep = 0;
                comboWindow = 0f;
                lungeTimer = 0f;
                StartDodge();
                return;
            }

            // 轻攻击允许格挡取消
            if (Input.GetKeyDown(KeyCode.F) && attackStep < 4)
            {
                attackTimer = 0f;
                attackStep = 0;
                comboWindow = 0f;
                lungeTimer = 0f;
                PerformBlock();
                return;
            }

            // 预输入接下一段轻攻击
            if (Input.GetKeyDown(KeyCode.J) || Input.GetMouseButtonDown(0))
            {
                if (attackTimer < 0.18f && attackStep < 3)
                {
                    PerformNextAttack();
                    return;
                }
            }

            // 轻攻击派生重刺
            if (Input.GetKeyDown(KeyCode.K) || Input.GetMouseButtonDown(1))
            {
                if (attackTimer < 0.20f && (attackStep == 1 || attackStep == 2))
                {
                    PerformHeavyThrust();
                    return;
                }
            }
            return;
        }

        // 破空刺技能 (Q 或 U)
        if (Input.GetKeyDown(KeyCode.Q) || Input.GetKeyDown(KeyCode.U))
        {
            TriggerPokongci();
            return;
        }

        // 回风舞技能 (E 或 O)
        if (Input.GetKeyDown(KeyCode.E) || Input.GetKeyDown(KeyCode.O))
        {
            TriggerHuifengwu();
            return;
        }

        // 一剑霜寒技能 (I)
        if (Input.GetKeyDown(KeyCode.I))
        {
            TriggerYijianshuanghan();
            return;
        }

        // 跳跃 (W / Up / W+Space)
        bool jumpInput = Input.GetKeyDown(KeyCode.W) || Input.GetKeyDown(KeyCode.UpArrow) || (Input.GetKey(KeyCode.W) && Input.GetKeyDown(KeyCode.Space));
        if (jumpInput && isGrounded && dodgeTimer <= 0f)
        {
            isGrounded = false;
            velY = JumpVelocity;
            currentActionName = "跳跃 (Jump)";
            if (animator != null)
            {
                animator.SetBool("IsGrounded", false);
                animator.SetTrigger("Jump");
            }
        }

        // 闪避 (Space，未按住 W)
        if (Input.GetKeyDown(KeyCode.Space) && !Input.GetKey(KeyCode.W))
        {
            StartDodge();
            return;
        }

        // 格挡架势 (F)
        if (Input.GetKeyDown(KeyCode.F) && isGrounded && dodgeTimer <= 0f)
        {
            PerformBlock();
            return;
        }

        // 普通格挡受击响应 (G)
        if (Input.GetKeyDown(KeyCode.G) && isGrounded && dodgeTimer <= 0f)
        {
            TriggerBlockHit();
            return;
        }

        // 完美弹反成功响应 (T)
        if (Input.GetKeyDown(KeyCode.T) && isGrounded && dodgeTimer <= 0f)
        {
            TriggerParrySuccess();
            return;
        }

        // 重刺 (K 或 鼠标右键)
        if (Input.GetKeyDown(KeyCode.K) || Input.GetMouseButtonDown(1))
        {
            PerformHeavyThrust();
            return;
        }

        // 轻攻击三连斩 (J 或 鼠标左键)
        if (Input.GetKeyDown(KeyCode.J) || Input.GetMouseButtonDown(0))
        {
            PerformNextAttack();
            return;
        }

        // 水平位移与行走/奔跑
        float mx = 0f;
        if (Input.GetKey(KeyCode.A) || Input.GetKey(KeyCode.LeftArrow)) mx -= 1f;
        if (Input.GetKey(KeyCode.D) || Input.GetKey(KeyCode.RightArrow)) mx += 1f;
        bool sprint = Input.GetKey(KeyCode.LeftShift) || Input.GetKey(KeyCode.RightShift);

        float animSpeed = 0f;
        float moveSpeed = QingfengWalkStride.DesignMoveSpeed;
        if (Mathf.Abs(mx) > WalkThreshold)
        {
            if (sprint)
            {
                animSpeed = 1f;
                moveSpeed = QingfengRunStride.DesignMoveSpeed;
                currentActionName = "奔跑 (Run)";
            }
            else
            {
                animSpeed = WalkAnimSpeed;
                moveSpeed = QingfengWalkStride.DesignMoveSpeed;
                currentActionName = "行走 (Walk)";
            }
        }
        else
        {
            if (isGrounded && attackTimer <= 0f && blockTimer <= 0f && dodgeTimer <= 0f)
                currentActionName = "待机 (Idle)";
        }

        if (animator != null) animator.SetFloat("Speed", animSpeed);

        if (Mathf.Abs(mx) > WalkThreshold)
        {
            if (spriteRenderer != null) spriteRenderer.flipX = mx < 0f;
            Vector3 p = transform.position;
            float airFactor = isGrounded ? 1f : 0.8f;
            p.x += mx * moveSpeed * airFactor * Time.deltaTime;
            transform.position = p;
        }
    }

    public void StartDodge()
    {
        dodgeDir = spriteRenderer != null && spriteRenderer.flipX ? -1f : 1f;
        if (Input.GetKey(KeyCode.A) || Input.GetKey(KeyCode.LeftArrow)) dodgeDir = -1f;
        if (Input.GetKey(KeyCode.D) || Input.GetKey(KeyCode.RightArrow)) dodgeDir = 1f;
        if (spriteRenderer != null) spriteRenderer.flipX = dodgeDir < 0f;

        dodgeTimer = DodgeDuration;
        currentActionName = "闪避 (Dodge)";
        if (animator != null) animator.SetTrigger("Dodge");
    }

    public void PerformNextAttack()
    {
        if (attackStep == 0 || comboWindow <= 0f)
        {
            attackStep = 1;
            attackTimer = 0.34f;
            comboWindow = 0.55f;
            lungeTimer = 0.10f;
            lungeSpeed = 0.15f / 0.10f;
            currentActionName = "轻攻击一段 (Attack 1)";
            if (animator != null) animator.SetTrigger("Attack1");
        }
        else if (attackStep == 1)
        {
            attackStep = 2;
            attackTimer = 0.34f;
            comboWindow = 0.55f;
            lungeTimer = 0.10f;
            lungeSpeed = 0.20f / 0.10f;
            currentActionName = "轻攻击二段 (Attack 2)";
            if (animator != null) animator.SetTrigger("Attack2");
        }
        else if (attackStep == 2)
        {
            attackStep = 3;
            attackTimer = 0.38f;
            comboWindow = 0f;
            lungeTimer = 0.12f;
            lungeSpeed = 0.25f / 0.12f;
            currentActionName = "轻攻击三段 (Attack 3)";
            if (animator != null) animator.SetTrigger("Attack3");
        }
    }

    public void PerformHeavyThrust()
    {
        attackStep = 4;
        attackTimer = 0.76f;
        comboWindow = 0f;
        lungeTimer = 0.18f;
        lungeSpeed = 0.40f / 0.18f;
        currentActionName = "蓄力重刺 (Heavy Thrust)";
        if (animator != null) animator.SetTrigger("HeavyThrust");
    }

    public void PerformBlock()
    {
        attackStep = 0;
        attackTimer = 0f;
        comboWindow = 0f;
        lungeTimer = 0f;
        blockTimer = BlockDuration;
        currentActionName = "格挡姿态 (Block Guard)";
        if (animator != null) animator.SetTrigger("Block");
    }

    public void TriggerBlockHit()
    {
        attackStep = 0;
        attackTimer = 0f;
        comboWindow = 0f;
        lungeTimer = 0f;
        blockTimer = 0.30f;
        currentActionName = "普通格挡受击 (Block Hit)";
        if (animator != null) animator.SetTrigger("BlockHit");
    }

    public void TriggerParrySuccess()
    {
        attackStep = 0;
        attackTimer = 0f;
        comboWindow = 0f;
        lungeTimer = 0f;
        blockTimer = 0.50f;
        currentActionName = "完美弹反成功 (Parry Success)";
        if (animator != null) animator.SetTrigger("ParrySuccess");
    }

    public int swordIntent = 5; // 默认满额 5 阶剑意便于预览绽放
    bool isBloomActive => swordIntent >= 5;

    public void TriggerPokongci()
    {
        if (isSkillPlaying) return;
        attackStep = 0;
        attackTimer = 0f;
        comboWindow = 0f;
        blockTimer = 0f;
        dodgeTimer = 0f;
        if (isBloomActive)
        {
            StartCoroutine(PokongciBloomRoutine());
        }
        else
        {
            StartCoroutine(PokongciRoutine());
        }
    }

    public void TriggerPokongciBloom()
    {
        if (isSkillPlaying) return;
        swordIntent = 5;
        attackStep = 0;
        attackTimer = 0f;
        comboWindow = 0f;
        blockTimer = 0f;
        dodgeTimer = 0f;
        StartCoroutine(PokongciBloomRoutine());
    }

    IEnumerator PokongciRoutine()
    {
        isSkillPlaying = true;
        currentActionName = "【剑技】破空刺 · 错身瞬透 (Piercing Void Thrust)";

        Vector3 startP = transform.position;
        float faceDir = spriteRenderer != null && spriteRenderer.flipX ? -1f : 1f;
        Vector3 targetEndP = startP + new Vector3(faceDir * 1.3f, 0f, 0f);
        Sprite activeSp = spriteRenderer != null ? spriteRenderer.sprite : null;

        // 启动常态破空刺专属特效（细青白激光线 + 2重残影 + 敌后延时裂体墨爆）
        PokongciBloomFX.Instance.PlayNormalPokongciFX(transform, spriteRenderer != null && spriteRenderer.flipX, startP, targetEndP, activeSp);

        if (pokongciSprites != null && pokongciSprites.Length >= 7)
        {
            if (animator != null) animator.enabled = false;

            // 极速起手(5f) -> 电光穿透(3f, +1.3m穿透敌后) -> 敌后单膝刹车(4f) -> 抽剑旋腕(5f)
            float[] frameDurations = new float[] { 0.04f, 0.04f, 0.04f, 0.05f, 0.06f, 0.07f, 0.06f };
            float[] frameLunges = new float[] { 0f, 0.25f, 0.70f, 0.35f, 0.0f, 0.0f, 0.0f }; // 总位移 1.3m，直接穿透至敌后

            for (int i = 0; i < 7; i++)
            {
                if (spriteRenderer != null) spriteRenderer.sprite = pokongciSprites[i];
                float duration = frameDurations[i];
                float lunge = frameLunges[i];
                float elapsed = 0f;
                while (elapsed < duration)
                {
                    float dt = Time.deltaTime;
                    elapsed += dt;
                    if (lunge > 0f && duration > 0f)
                    {
                        Vector3 p = transform.position;
                        p.x += faceDir * (lunge / duration) * dt;
                        transform.position = p;
                    }
                    yield return null;
                }
            }
            if (animator != null) animator.enabled = true;
        }
        else
        {
            PerformHeavyThrust();
            yield return new WaitForSeconds(0.40f);
        }

        isSkillPlaying = false;
        currentActionName = "待机 (Idle)";
    }

    IEnumerator PokongciBloomRoutine()
    {
        isSkillPlaying = true;
        currentActionName = "【剑意绽放】极·破空刺 (Void Thrust · Bloom)";
        swordIntent = 0; // 消耗 5 阶剑意

        Vector3 startP = transform.position;
        float faceDir = spriteRenderer != null && spriteRenderer.flipX ? -1f : 1f;
        Vector3 targetEndP = startP + new Vector3(faceDir * 1.8f, 0f, 0f);
        Sprite activeSp = spriteRenderer != null ? spriteRenderer.sprite : null;

        // 启动电影级全套特效（四灵飞剑+天崩巨锥+时空停滞+三度墨爆+空间裂隙+冰霜霜痕+残影）
        PokongciBloomFX.Instance.PlayBloomEffect(transform, spriteRenderer != null && spriteRenderer.flipX, startP, targetEndP, activeSp);

        if (pokongciSprites != null && pokongciSprites.Length >= 7)
        {
            if (animator != null) animator.enabled = false;

            // 刚体聚势闪烁 (青金刚体光辉)
            if (spriteRenderer != null) spriteRenderer.color = new Color(0.6f, 1f, 1f, 1f);

            // 强化版位移翻倍至 1.8m，穿透一切敌人
            float[] frameDurations = new float[] { 0.06f, 0.05f, 0.05f, 0.08f, 0.06f, 0.08f, 0.06f };
            float[] frameLunges = new float[] { 0f, 0.4f, 0.9f, 0.5f, 0.0f, 0.0f, 0.0f }; // 总位移 1.8m

            // P1~P3 聚势与离弦
            for (int i = 0; i < 3; i++)
            {
                if (spriteRenderer != null) spriteRenderer.sprite = pokongciSprites[i];
                float duration = frameDurations[i];
                float lunge = frameLunges[i];
                float elapsed = 0f;
                while (elapsed < duration)
                {
                    float dt = Time.deltaTime;
                    elapsed += dt;
                    if (lunge > 0f && duration > 0f)
                    {
                        Vector3 p = transform.position;
                        p.x += faceDir * (lunge / duration) * dt;
                        transform.position = p;
                    }
                    yield return null;
                }
            }

            // P4 瞬身穿透 + 6f 时空静止 (Chrono Pause)
            if (spriteRenderer != null)
            {
                spriteRenderer.sprite = pokongciSprites[3];
                spriteRenderer.color = Color.white;
            }
            float lungeP4 = frameLunges[3];
            float durP4 = frameDurations[3];
            float elP4 = 0f;
            while (elP4 < durP4)
            {
                float dt = Time.deltaTime;
                elP4 += dt;
                Vector3 p = transform.position;
                p.x += faceDir * (lungeP4 / durP4) * dt;
                transform.position = p;
                yield return null;
            }

            // 穿透至敌后：时空慢放 0.1s
            Time.timeScale = 0.2f;
            yield return new WaitForSecondsRealtime(0.10f);
            Time.timeScale = 1.0f;

            // P5 裂痕蓄爆与共振
            if (spriteRenderer != null) spriteRenderer.sprite = pokongciSprites[4];
            yield return new WaitForSeconds(0.06f);

            // P6 三度连环墨爆 (三次闪烁与音画震颤)
            currentActionName = "【剑痕引爆】三度断空墨爆！";
            for (int blast = 1; blast <= 3; blast++)
            {
                if (spriteRenderer != null) spriteRenderer.color = new Color(0.3f, 0.9f, 1f);
                yield return new WaitForSeconds(0.04f);
                if (spriteRenderer != null) spriteRenderer.color = Color.white;
                yield return new WaitForSeconds(0.03f);
            }

            // P7 散尘纳鞘与冰霜余韵
            if (spriteRenderer != null) spriteRenderer.sprite = pokongciSprites[5];
            yield return new WaitForSeconds(frameDurations[5]);
            if (spriteRenderer != null) spriteRenderer.sprite = pokongciSprites[6];
            yield return new WaitForSeconds(frameDurations[6]);

            if (animator != null) animator.enabled = true;
        }
        else
        {
            PerformHeavyThrust();
            yield return new WaitForSeconds(0.6f);
        }

        if (spriteRenderer != null) spriteRenderer.color = Color.white;
        isSkillPlaying = false;
        currentActionName = "待机 (Idle)";
    }

    public void TriggerHuifengwu()
    {
        if (isSkillPlaying) return;
        if (huifengwuSprites == null || huifengwuSprites.Length < 8 || huifengwuSprites[0] == null)
        {
            LoadHuifengwuSprites();
        }
        attackStep = 0;
        attackTimer = 0f;
        comboWindow = 0f;
        blockTimer = 0f;
        dodgeTimer = 0f;
        if (isBloomActive)
        {
            StartCoroutine(HuifengwuRoutine(true));
        }
        else
        {
            StartCoroutine(HuifengwuRoutine(false));
        }
    }

    public void TriggerHuifengwuBloom()
    {
        if (isSkillPlaying) return;
        if (huifengwuSprites == null || huifengwuSprites.Length < 8 || huifengwuSprites[0] == null)
        {
            LoadHuifengwuSprites();
        }
        swordIntent = 5;
        attackStep = 0;
        attackTimer = 0f;
        comboWindow = 0f;
        blockTimer = 0f;
        dodgeTimer = 0f;
        StartCoroutine(HuifengwuRoutine(true));
    }

    IEnumerator HuifengwuRoutine(bool isBloom)
    {
        isSkillPlaying = true;
        currentActionName = isBloom ? "剑意·回风舞（青鸾风暴）" : "回风舞 (Whirling Wind Dance)";
        if (isBloom) swordIntent = 0;

        if (huifengwuSprites == null || huifengwuSprites.Length < 8 || huifengwuSprites[0] == null)
        {
            LoadHuifengwuSprites();
        }

        if (animator != null) animator.enabled = false;

        // 触发回风舞专属特效（月牙斩芒、交错斩光与剑尖星爆）
        PokongciBloomFX.Instance.PlayHuifengwuFX(transform, isBloom);

        Vector3 basePos = transform.position;
        bool origFlip = spriteRenderer != null && spriteRenderer.flipX;

        if (huifengwuSprites != null && huifengwuSprites.Length >= 8 && huifengwuSprites[0] != null)
        {
            // 60 FPS 8阶段完整双手挥剑动作帧时序：
            // F1: 拧腰蓄剑 (attack-5 手臂高提蓄劲)
            // F2: 旋身撩剑 (attack-7 双手向上猛挑撩斩)
            // F3: 剑轮初开 (attack-3 手臂全力舒展横斩)
            // F4: 展袖换势 (attack-8 双手回带转剑流光)
            // F5: 双层风暴 (attack-11 360°双手全力回旋怒挥重斩)
            // F6: 侧步插剑 (attack-6 双手沉剑下劈定风)
            // F7: 挽花收剑 (attack-12 手腕轻抖挽水墨剑花)
            // F8: 拂袖敛意 (attack-4 双手持剑秋水入鞘)
            float[] frameDurations = isBloom
                ? new float[] { 0.07f, 0.08f, 0.08f, 0.06f, 0.09f, 0.08f, 0.08f, 0.09f }
                : new float[] { 0.067f, 0.083f, 0.067f, 0.050f, 0.067f, 0.083f, 0.083f, 0.100f };

            // 绽放形态全身青光荧华
            if (isBloom && spriteRenderer != null)
            {
                spriteRenderer.color = new Color(0.65f, 1f, 1f, 1f);
            }

            for (int i = 0; i < 8; i++)
            {
                if (spriteRenderer != null)
                {
                    spriteRenderer.sprite = huifengwuSprites[i];
                }

                // F4~F5 微腾空跃起 0.15m~0.25m
                if (i == 3 || i == 4)
                {
                    float hop = isBloom ? 0.22f : 0.14f;
                    transform.position = new Vector3(basePos.x, basePos.y + hop, basePos.z);
                }
                else
                {
                    transform.position = basePos;
                }

                // 强化形态在 F3 和 F5 判定命中瞬间进行轻微画面顿帧 (Hitstop)
                if (isBloom && (i == 2 || i == 4))
                {
                    Time.timeScale = 0.25f;
                    yield return new WaitForSecondsRealtime(0.04f);
                    Time.timeScale = 1.0f;
                }

                yield return new WaitForSeconds(frameDurations[i]);
            }
        }
        else
        {
            // 备用降级：如果精灵帧未就绪，强制调用 Animator 播放实打实的普通连斩动画，绝不静止待机！
            if (animator != null)
            {
                animator.enabled = true;
                animator.Play("Attack1", 0, 0f);
                yield return new WaitForSeconds(0.12f);
                animator.Play("Attack2", 0, 0f);
                yield return new WaitForSeconds(0.14f);
                animator.Play("Attack3", 0, 0f);
                yield return new WaitForSeconds(0.20f);
            }
            else
            {
                yield return new WaitForSeconds(0.35f);
            }
        }

        transform.position = basePos;
        if (spriteRenderer != null)
        {
            spriteRenderer.flipX = origFlip;
            spriteRenderer.color = Color.white;
        }

        if (animator != null) animator.enabled = true;
        isSkillPlaying = false;
        currentActionName = "待机 (Idle)";
    }

    public void TriggerYijianshuanghan()
    {
        if (isSkillPlaying) return;
        if (yijianshuanghanSprites == null || yijianshuanghanSprites.Length < 8 || yijianshuanghanSprites[0] == null)
        {
            LoadYijianshuanghanSprites();
        }
        attackStep = 0;
        attackTimer = 0f;
        comboWindow = 0f;
        blockTimer = 0f;
        dodgeTimer = 0f;
        StartCoroutine(YijianshuanghanRoutine());
    }

    IEnumerator YijianshuanghanRoutine()
    {
        isSkillPlaying = true;
        currentActionName = "一剑霜寒 (Frostbound Slash · 蓄力霜线)";

        if (yijianshuanghanSprites == null || yijianshuanghanSprites.Length < 8 || yijianshuanghanSprites[0] == null)
        {
            LoadYijianshuanghanSprites();
        }

        if (animator != null) animator.enabled = false;

        Vector3 basePos = transform.position;
        bool origFlip = spriteRenderer != null && spriteRenderer.flipX;
        float faceDir = origFlip ? -1f : 1f;

        if (yijianshuanghanSprites != null && yijianshuanghanSprites.Length >= 8 && yijianshuanghanSprites[0] != null)
        {
            // 8阶段时序：
            // F1: 结势·冰霜凝聚 (0.10s)
            // F2: 提剑·寒气汇聚 (0.13s)
            // F3: 蓄力·冰刃成型 (0.18s)
            // F4: 斩出·霜寒剑芒 (0.09s, 击中顿帧)
            // F5: 前刺·冰锋破地 (0.11s, 前冲微位移 0.35m)
            // F6: 进步·寒气延绵 (0.13s)
            // F7: 振刃·冰晶碎散 (0.13s)
            // F8: 入鞘·风息归平 (0.16s)
            float[] frameDurations = new float[] { 0.10f, 0.13f, 0.18f, 0.09f, 0.11f, 0.13f, 0.13f, 0.16f };

            for (int i = 0; i < 8; i++)
            {
                if (spriteRenderer != null)
                {
                    spriteRenderer.sprite = yijianshuanghanSprites[i];
                }

                // F4 斩出瞬间 Hitstop (顿帧)
                if (i == 3)
                {
                    Time.timeScale = 0.25f;
                    yield return new WaitForSecondsRealtime(0.04f);
                    Time.timeScale = 1.0f;
                }

                // F5 前刺冲刷微位移
                if (i == 4)
                {
                    Vector3 p = transform.position;
                    p.x += faceDir * 0.35f;
                    transform.position = p;
                }

                yield return new WaitForSeconds(frameDurations[i]);
            }
        }
        else
        {
            if (animator != null)
            {
                animator.enabled = true;
                animator.Play("HeavyThrust", 0, 0f);
            }
            yield return new WaitForSeconds(0.6f);
        }

        if (spriteRenderer != null)
        {
            spriteRenderer.flipX = origFlip;
            spriteRenderer.color = Color.white;
        }

        if (animator != null) animator.enabled = true;
        isSkillPlaying = false;
        currentActionName = "待机 (Idle)";
    }

    void OnGUI()
    {
        // 仅在独立预览模式下绘制操控面板
        if (combat != null) return;

        GUILayout.BeginArea(new Rect(20, 20, 390, 510), GUI.skin.box);
        GUILayout.Label("<b><size=15>【刀影江湖 · 青锋动作与技能预览台】</size></b>");
        GUILayout.Space(4);
        GUILayout.Label($"<b>当前动作：</b><color=#00ff88>{currentActionName}</color>");
        GUILayout.Label($"<b>剑意状态：</b>[ <color=#00e1ff>{new string('★', swordIntent)}{new string('☆', 5 - swordIntent)}</color> ({swordIntent}/5阶) ]  " +
                        $"<color={(isBloomActive ? "#ffff00" : "#aaaaaa")}><b>{(isBloomActive ? "【剑意澄澈·可绽放】" : "蓄力中")}</b></color>");
        GUILayout.Label($"<b>接地状态：</b>{(isGrounded ? "已在地面" : "空中升降")} | <b>格挡：</b>{(IsBlocking ? "格挡中" : "无")}");
        GUILayout.Space(4);

        // 剑意充能切换
        GUILayout.BeginHorizontal();
        if (GUILayout.Button("重置剑意(0)")) swordIntent = 0;
        if (GUILayout.Button("+1层剑意")) swordIntent = Mathf.Min(5, swordIntent + 1);
        GUI.color = new Color(1f, 0.9f, 0.2f);
        if (GUILayout.Button("充能满额(5阶绽放)")) swordIntent = 5;
        GUI.color = Color.white;
        GUILayout.EndHorizontal();

        GUILayout.Space(6);
        GUILayout.Label("<b>--- 技能1：破空刺 (瞬身错身穿透 Q/U) ---</b>");
        GUILayout.BeginHorizontal();
        GUI.color = new Color(0.4f, 1f, 1f);
        if (GUILayout.Button("常态错身刺 (穿透1.3m+延时墨爆)", GUILayout.Height(30)))
        {
            StartCoroutine(PokongciRoutine());
        }
        GUI.color = new Color(1f, 0.8f, 0.1f);
        if (GUILayout.Button("★ 极·破空刺 (无敌1.8m+四剑+三度爆)", GUILayout.Height(30)))
        {
            TriggerPokongciBloom();
        }
        GUI.color = Color.white;
        GUILayout.EndHorizontal();

        GUILayout.Space(6);
        GUILayout.Label("<b>--- 技能2：回风舞 (360°旋风范围解围 E/O) ---</b>");
        GUILayout.BeginHorizontal();
        GUI.color = new Color(0.3f, 0.95f, 1f);
        if (GUILayout.Button("常态回风舞 (双层剑轮+微聚怪)", GUILayout.Height(30)))
        {
            TriggerHuifengwu();
        }
        GUI.color = new Color(1f, 0.85f, 0.2f);
        if (GUILayout.Button("★ 青鸾风暴·回风舞 (黑洞5段绞杀)", GUILayout.Height(30)))
        {
            TriggerHuifengwuBloom();
        }
        GUI.color = Color.white;
        GUILayout.EndHorizontal();

        GUILayout.Space(6);
        GUILayout.Label("<b>--- 技能3：一剑霜寒 (长距离蓄力破防霜线 I) ---</b>");
        GUILayout.BeginHorizontal();
        GUI.color = new Color(0.45f, 0.85f, 1f);
        if (GUILayout.Button("一剑霜寒 (8阶段蓄力破防霜线斩 I)", GUILayout.Height(30)))
        {
            TriggerYijianshuanghan();
        }
        GUI.color = Color.white;
        GUILayout.EndHorizontal();

        GUILayout.Space(6);
        GUILayout.Label("<b>--- 基础连击与招式 (点击或按键) ---</b>");
        GUILayout.BeginHorizontal();
        if (GUILayout.Button("轻击1 (J)")) PerformNextAttack();
        if (GUILayout.Button("轻击2 (J)")) { attackStep = 1; PerformNextAttack(); }
        if (GUILayout.Button("轻击3 (J)")) { attackStep = 2; PerformNextAttack(); }
        if (GUILayout.Button("重刺 (K)")) PerformHeavyThrust();
        GUILayout.EndHorizontal();

        GUILayout.Space(6);
        GUILayout.Label("<b>--- 防守与身法 ---</b>");
        GUILayout.BeginHorizontal();
        if (GUILayout.Button("格挡(F)")) PerformBlock();
        if (GUILayout.Button("受击(G)")) TriggerBlockHit();
        if (GUILayout.Button("弹反(T)")) TriggerParrySuccess();
        if (GUILayout.Button("闪避(Space)")) StartDodge();
        if (GUILayout.Button("跳跃(W)"))
        {
            if (isGrounded)
            {
                isGrounded = false;
                velY = JumpVelocity;
                if (animator != null) { animator.SetBool("IsGrounded", false); animator.SetTrigger("Jump"); }
            }
        }
        GUILayout.EndHorizontal();

        GUILayout.Space(6);
        GUILayout.Label("<color=#cccccc><size=11>按键提示：Q/U 释放破空刺（满5层剑意自动触发绽放强化版）\nA/D 行走 | Shift+A/D 奔跑 | W 跳跃 | Space 闪避 | J 轻击三连 | K 重刺</size></color>");
        GUILayout.EndArea();
    }
}
