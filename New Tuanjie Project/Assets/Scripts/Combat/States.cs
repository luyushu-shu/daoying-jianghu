using System.Collections.Generic;
using UnityEngine;

/// <summary>状态基类。Frame 为 1 起始的帧计数，与帧数据表对齐。</summary>
public abstract class ActorState
{
    protected CombatActor actor;
    public string Name;
    public int Frame;

    protected ActorState(CombatActor a, string n) { actor = a; Name = n; }
    public virtual void Enter() { Frame = 0; }
    public virtual void Tick() { Frame++; }
    public virtual void Exit() { }
}

/// <summary>地面：站立/奔跑。攻击意图仅玩家在此映射；敌人由 AI 直接切状态。</summary>
public class GroundedState : ActorState
{
    int landRecovery;

    public GroundedState(CombatActor a, int landRecoveryFrames = 0) : base(a, "Grounded") { landRecovery = landRecoveryFrames; }

    public override void Tick()
    {
        base.Tick();
        if (landRecovery > 0) landRecovery--;

        actor.body.vel.x = actor.inp.moveX * actor.runSpeed;
        if (actor.isPlayer && Mathf.Abs(actor.inp.moveX) > 0.01f)
            actor.facing = actor.inp.moveX > 0 ? 1 : -1;

        if (!actor.body.grounded && actor.body.vel.y <= 0f)
        {
            actor.ChangeState(new AirborneState(actor, false));
            return;
        }

        if (!actor.isPlayer) return;
        if (landRecovery > 0) return;

        if (actor.inp.blockHeld) { actor.ChangeState(new BlockState(actor)); return; }
        if (actor.inp.dodge) { actor.Consume("dodge"); actor.ChangeState(new DodgeState(actor, false)); return; }
        if (actor.inp.jump) { actor.Consume("jump"); actor.ChangeState(new AirborneState(actor, true)); return; }
        if (actor.inp.dash) { actor.Consume("dash"); actor.ChangeState(new DashState(actor)); return; }
        if (actor.inp.light) { actor.Consume("light"); PlayerChains.StartLight(actor, null); return; }
        if (actor.inp.heavy) { actor.Consume("heavy"); PlayerChains.StartHeavy(actor, null); return; }
        if (actor.inp.skill1) { actor.Consume("skill1"); PlayerChains.StartSkill(actor, "QF-1"); return; }
        if (actor.inp.skill2) { actor.Consume("skill2"); PlayerChains.StartSkill(actor, "QF-3"); return; }
    }
}

/// <summary>空中：含起跳深蹲3f与自由下落。</summary>
public class AirborneState : ActorState
{
    int jumpSquat;

    public AirborneState(CombatActor a, bool jump) : base(a, "Airborne") { jumpSquat = jump ? 3 : 0; }

    public override void Enter()
    {
        base.Enter();
        if (jumpSquat > 0) actor.body.vel.y = 0f;
    }

    public override void Tick()
    {
        base.Tick();
        actor.body.vel.x = actor.inp.moveX * actor.runSpeed * 0.8f;
        if (actor.isPlayer && Mathf.Abs(actor.inp.moveX) > 0.01f)
            actor.facing = actor.inp.moveX > 0 ? 1 : -1;

        if (jumpSquat > 0)
        {
            jumpSquat--;
            actor.body.vel.y = 0f;
            if (jumpSquat == 0) actor.body.vel.y = actor.jumpVel;
            return;
        }

        if (actor.body.grounded && actor.body.vel.y <= 0f)
        {
            actor.ChangeState(new GroundedState(actor, 4));
            return;
        }

        if (!actor.isPlayer) return;

        if (actor.inp.dodge && !actor.airDodgeUsed) { actor.Consume("dodge"); actor.ChangeState(new DodgeState(actor, true)); return; }
        if (actor.inp.light) { actor.Consume("light"); PlayerChains.StartLight(actor, null); return; }
        if (actor.inp.heavy) { actor.Consume("heavy"); PlayerChains.StartHeavy(actor, null); return; }
    }
}

/// <summary>冲刺：10f，可接冲刺攻击或闪避。</summary>
public class DashState : ActorState
{
    const int Duration = 10;

    public DashState(CombatActor a) : base(a, "Dash") { }

    public override void Tick()
    {
        base.Tick();
        actor.body.vel.x = actor.facing * actor.runSpeed * 1.6f;

        if (actor.isPlayer)
        {
            if (actor.inp.light) { actor.Consume("light"); PlayerChains.StartLight(actor, "DASH"); return; }
            if (actor.inp.heavy) { actor.Consume("heavy"); PlayerChains.StartHeavy(actor, "DASH"); return; }
            if (actor.inp.dodge) { actor.Consume("dodge"); actor.ChangeState(new DodgeState(actor, false)); return; }
        }

        if (Frame >= Duration) actor.ChangeState(new GroundedState(actor));
    }
}

/// <summary>闪避：无敌帧由帧数据表 ifStart/ifEnd 给出。</summary>
public class DodgeState : ActorState
{
    readonly bool air;
    readonly MoveData mv;
    int dir;

    public DodgeState(CombatActor a, bool air) : base(a, air ? "AirDodge" : "Dodge")
    {
        this.air = air;
        mv = MoveDatabase.Get(air ? "MOV-AIRDODGE" : "MOV-DODGE");
    }

    public bool IFramesActive { get { return mv != null && Frame >= mv.ifStart && Frame <= mv.ifEnd; } }

    public override void Enter()
    {
        base.Enter();
        dir = Mathf.Abs(actor.inp.moveX) > 0.01f ? (int)Mathf.Sign(actor.inp.moveX) : actor.facing;
        if (air) actor.airDodgeUsed = true;
        actor.TriggerAnim("Dodge");
    }

    public override void Tick()
    {
        base.Tick();
        if (mv == null) { actor.ChangeState(new GroundedState(actor)); return; }

        // 位移：略微前移一小段（约 0.45 单位），在闪避前半段走完，后半段着地收招
        if (Frame >= mv.startup && Frame <= 7)
        {
            float lungeFrames = 7 - mv.startup + 1;
            float speed = mv.lunge / (lungeFrames / 60f);
            actor.body.vel.x = dir * speed;
            if (air) actor.body.vel.y = 0f;
        }
        else if (!air) actor.body.vel.x *= 0.6f;

        // 取消窗：可接攻击
        if (actor.isPlayer && mv.InCancelWindow(Frame))
        {
            if (actor.inp.light) { actor.Consume("light"); PlayerChains.StartLight(actor, null); return; }
            if (actor.inp.heavy) { actor.Consume("heavy"); PlayerChains.StartHeavy(actor, null); return; }
            if (actor.inp.skill1) { actor.Consume("skill1"); PlayerChains.StartSkill(actor, "QF-1"); return; }
        }

        if (Frame >= mv.Total)
        {
            if (air && !actor.body.grounded) actor.ChangeState(new AirborneState(actor, false));
            else actor.ChangeState(new GroundedState(actor));
        }
    }
}

/// <summary>攻击/技能：完全由帧数据驱动。判定、取消、霸体、蓄力、下砸都在此。</summary>
public class AttackState : ActorState
{
    public readonly MoveData Move;
    readonly HashSet<CombatActor> hitSetA = new HashSet<CombatActor>();
    readonly HashSet<CombatActor> hitSetB = new HashSet<CombatActor>();
    int chargeFrames;
    float dmgScale = 1f;
    float lungeSpeed;
    int totalFrames;
    bool bloomSpent;
    bool landed;

    public AttackState(CombatActor a, MoveData mv) : base(a, mv.id)
    {
        Move = mv;
    }

    public bool InStartup { get { return Frame <= Move.startup; } }
    public bool InActive
    {
        get
        {
            if (Move.HasTag("airDown") && Frame > Move.startup && !landed) return true;
            return Frame > Move.startup && Frame <= Move.startup + Move.active;
        }
    }
    public bool InArmorFrames
    {
        get { return Move.armorFrom > 0 && Frame >= Move.armorFrom && Frame <= Move.armorTo + chargeFrames; }
    }
    public float StartupProgress { get { return Move.startup <= 0 ? 1f : Mathf.Clamp01((float)Frame / Move.startup); } }

    public override void Enter()
    {
        base.Enter();
        actor.chi -= Move.chi;

        // 触发攻击动画（轻击三连斩）
        if (Move.id == "A_L1") actor.TriggerAnim("Attack1");
        else if (Move.id == "A_L2") actor.TriggerAnim("Attack2");
        else if (Move.id == "A_L3") actor.TriggerAnim("Attack3");
        else actor.TriggerAnim("Attack1");

        // 剑意绽放：该击后摇-4f
        int bloomBonus = (actor.isPlayer && actor.bloomArmed) ? 4 : 0;
        totalFrames = Move.Total - bloomBonus;

        // 前冲速度：在前摇后半+判定期内走完 lunge 距离
        float lungeFrames = Move.startup * 0.5f + Mathf.Max(1, Move.active);
        lungeSpeed = Move.lunge / (lungeFrames / 60f);
    }

    public override void Tick()
    {
        base.Tick();

        // 蓄力（一剑霜寒）：按住技能键延长前摇，伤害3.0→3.8
        if (Move.HasTag("chargeable") && Frame >= Move.startup && actor.inp.skill2Held && chargeFrames < 40)
        {
            Frame = Move.startup;
            chargeFrames++;
            totalFrames = Move.Total + chargeFrames;
            dmgScale = Mathf.Lerp(3.0f, 3.8f, chargeFrames / 40f) / Move.damage;
            actor.body.vel.x = 0f;
            return;
        }

        // 下重砸：判定持续到落地
        if (Move.HasTag("airDown") && Frame > Move.startup && !landed)
        {
            actor.body.vel.y = -20f;
            actor.body.vel.x = actor.facing * 1.5f;
            DoHitTest(hitSetA);
            if (actor.body.grounded)
            {
                landed = true;
                DoHitTest(hitSetA); // 落地震击
                CombatDirector.Shake(0.2f, 8);
                actor.body.vel.x = 0f;
                Frame = Move.startup + Move.active; // 进入后摇
            }
            return;
        }

        // 前冲位移
        if (Frame > Move.startup / 2 && Frame <= Move.startup + Move.active)
            actor.body.vel.x = actor.facing * lungeSpeed;
        else if (actor.body.grounded)
            actor.body.vel.x *= 0.5f;

        // 判定
        if (InActive) DoHitTest(hitSetA);
        if (Move.active2Start > 0 && Frame >= Move.active2Start && Frame <= Move.active2End) DoHitTest(hitSetB);

        // 取消
        if (actor.isPlayer && Move.InCancelWindow(Frame)) TryCancel();

        if (Frame >= totalFrames)
        {
            if (actor.body.grounded) actor.ChangeState(new GroundedState(actor));
            else actor.ChangeState(new AirborneState(actor, false));
        }
    }

    void TryCancel()
    {
        if (actor.inp.light && Move.CanCancelTo('L')) { actor.Consume("light"); PlayerChains.StartLight(actor, Move.id); return; }
        if (actor.inp.heavy && Move.CanCancelTo('H')) { actor.Consume("heavy"); PlayerChains.StartHeavy(actor, Move.id); return; }
        if (actor.inp.dodge && Move.CanCancelTo('D')) { actor.Consume("dodge"); actor.ChangeState(new DodgeState(actor, !actor.body.grounded)); return; }
        if (actor.inp.skill1 && Move.CanCancelTo('S')) { actor.Consume("skill1"); PlayerChains.StartSkill(actor, "QF-1"); return; }
        if (actor.inp.skill2 && Move.CanCancelTo('S')) { actor.Consume("skill2"); PlayerChains.StartSkill(actor, "QF-3"); return; }
    }

    void DoHitTest(HashSet<CombatActor> hitSet)
    {
        Vector2 center = Move.HasTag("centerSelf")
            ? actor.body.pos + new Vector2(0f, 1.0f)
            : actor.body.pos + new Vector2(actor.facing * Move.reach, 1.0f);

        List<CombatActor> all = CombatDirector.Actors;
        for (int i = 0; i < all.Count; i++)
        {
            CombatActor t = all[i];
            if (t == actor || t.isPlayer == actor.isPlayer || t.dead) continue;
            if (hitSet.Contains(t)) continue;

            Vector2 tc = t.body.pos + new Vector2(0f, 0.7f);
            if (Mathf.Abs(tc.x - center.x) <= (Move.boxW + 0.7f) * 0.5f &&
                Mathf.Abs(tc.y - center.y) <= (Move.boxH + 1.4f) * 0.5f)
            {
                hitSet.Add(t);

                // 剑意绽放：命中时消耗，伤害×1.35 架势×1.5
                float poiseScale = 1f;
                if (actor.isPlayer && actor.bloomArmed && !bloomSpent)
                {
                    bloomSpent = true;
                    actor.bloomArmed = false;
                    dmgScale *= 1.35f;
                    poiseScale = 1.5f;
                }

                HitInfo h = HitInfo.From(Move, actor, dmgScale * CombatDirector.DamageUnit, poiseScale);
                t.ApplyHit(h, actor);
            }
        }
    }
}

/// <summary>格挡：按住维持；按下后第6–10帧为弹反窗。</summary>
public class BlockState : ActorState
{
    public BlockState(CombatActor a) : base(a, "Block") { }

    public override void Tick()
    {
        base.Tick();
        actor.body.vel.x = actor.inp.moveX * actor.runSpeed * 0.35f;
        if (!actor.inp.blockHeld && Frame > 4)
            actor.ChangeState(new GroundedState(actor));
    }

    /// <summary>被命中时结算：弹反窗内=弹反，否则普通格挡。</summary>
    public void ResolveHit(HitInfo h, CombatActor attacker)
    {
        if (Frame >= 6 && Frame <= 10 && attacker != null)
        {
            // 弹反成功：敌招中断+28f硬直；霸体招额外给40架势
            attacker.ForceInterrupt(28, 40f);
            attacker.freezeFrames = Mathf.Max(attacker.freezeFrames, 4);
            actor.chi = Mathf.Min(actor.maxChi, actor.chi + 8f);
            actor.GainIntent(2);
            if (actor.intent >= 3) actor.ArmBloom();
            actor.freezeFrames = Mathf.Max(actor.freezeFrames, 2);
            CombatDirector.Msg("弹反!", actor.body.pos + new Vector2(0, 2f), new Color(1f, 0.85f, 0.3f), 45);
            CombatDirector.SlowMo(0.6f, 8);
            CombatDirector.Shake(0.18f, 8);
        }
        else
        {
            actor.hp -= h.damage * 0.15f;
            actor.freezeFrames = Mathf.Max(actor.freezeFrames, 2);
            if (attacker != null) attacker.freezeFrames = Mathf.Max(attacker.freezeFrames, 2);
            actor.body.vel.x = (attacker != null ? (int)Mathf.Sign(actor.body.pos.x - attacker.body.pos.x) : -actor.facing) * 2f;
            CombatDirector.Msg("格挡", actor.body.pos + new Vector2(0, 1.9f), new Color(0.7f, 0.8f, 0.9f), 25);
            if (actor.hp <= 0f) { actor.hp = 0f; actor.Die(); }
        }
    }
}

/// <summary>受击硬直。knockdown=true 为破防长硬直。</summary>
public class HitstunState : ActorState
{
    readonly int duration;
    public readonly bool knockdown;

    public HitstunState(CombatActor a, int duration, bool knockdown) : base(a, "Hitstun")
    {
        this.duration = duration;
        this.knockdown = knockdown;
    }

    public override void Tick()
    {
        base.Tick();
        actor.body.vel.x *= 0.85f;
        if (Frame >= duration)
        {
            actor.iframesUntil = CombatDirector.Frame + 12; // 起身无敌
            if (actor.body.grounded) actor.ChangeState(new GroundedState(actor));
            else actor.ChangeState(new AirborneState(actor, false));
        }
    }
}

/// <summary>死亡。</summary>
public class DeadState : ActorState
{
    public DeadState(CombatActor a) : base(a, "Dead") { }

    public override void Enter()
    {
        base.Enter();
        actor.body.vel = Vector2.zero;
    }

    public override void Tick()
    {
        base.Tick();
        if (!actor.isPlayer && Frame > 120f)
        {
            CombatDirector.Unregister(actor);
            Object.Destroy(actor.gameObject);
        }
    }
}

/// <summary>玩家连段解析：当前招式+意图 → 下一招。</summary>
public static class PlayerChains
{
    public static void StartLight(CombatActor a, string currentId)
    {
        string next;
        if (currentId == "DASH") next = "A_DA";
        else if (!a.body.grounded)
        {
            if (currentId == "A_AL1") next = "A_AL2";
            else if (currentId == null && a.airLightStep == 0) next = "A_AL1";
            else next = null;
        }
        else
        {
            if (currentId == null) next = "A_L1";
            else if (currentId == "A_L1") next = "A_L2";
            else if (currentId == "A_L2") next = "A_L3";
            else next = null;
        }
        if (next == null) return;
        MoveData mv = MoveDatabase.Get(next);
        if (mv == null) return;
        if (next == "A_AL1") a.airLightStep = 1;
        a.ChangeState(new AttackState(a, mv));
    }

    public static void StartHeavy(CombatActor a, string currentId)
    {
        string next;
        if (currentId == "DASH") next = "A_DH";
        else if (!a.body.grounded) next = currentId == null ? "A_AD" : null;
        else if (currentId == "A_L2") next = "A_L2H";
        else next = "A_H";
        if (next == null) return;
        MoveData mv = MoveDatabase.Get(next);
        if (mv == null) return;
        a.ChangeState(new AttackState(a, mv));
    }

    public static void StartSkill(CombatActor a, string id)
    {
        MoveData mv = MoveDatabase.Get(id);
        if (mv == null) return;
        if (a.chi < mv.chi)
        {
            CombatDirector.Msg("内力不足", a.body.pos + new Vector2(0, 1.9f), new Color(0.5f, 0.7f, 1f), 30);
            return;
        }
        a.ChangeState(new AttackState(a, mv));
    }
}
