using UnityEngine;

/// <summary>敌人脑基类：直接操作意图与状态切换（不走输入缓冲）。</summary>
public abstract class EnemyBrain : Brain
{
    protected int cooldown;
    protected int comboStep;

    protected CombatActor FindPlayer()
    {
        var all = CombatDirector.Actors;
        for (int i = 0; i < all.Count; i++)
            if (all[i].isPlayer && !all[i].dead) return all[i];
        return null;
    }

    protected bool Busy { get { return actor.state is AttackState || actor.state is HitstunState || actor.state is DodgeState; } }

    protected void StartAttack(string moveId)
    {
        MoveData mv = MoveDatabase.Get(moveId);
        if (mv != null) actor.ChangeState(new AttackState(actor, mv));
    }
}

/// <summary>
/// 杂兵刀手：两招连斩 + 偶发冲刺砍。教学目的：格挡与轻连（GDD §3.7）。
/// </summary>
public class SwordsmanBrain : EnemyBrain
{
    int retreatFrames;
    bool willCombo;

    public override void Think()
    {
        if (actor.dead) return;
        actor.inp.moveX = 0f;
        if (cooldown > 0) cooldown--;

        CombatActor player = FindPlayer();
        if (player == null) return;
        if (Busy) return;

        float dx = player.FeetPos.x - actor.FeetPos.x;
        float adx = Mathf.Abs(dx);
        int dir = dx >= 0f ? 1 : -1;

        if (!(actor.state is GroundedState)) return;
        actor.facing = dir;

        // 连斩第二下
        if (comboStep == 1)
        {
            comboStep = 0;
            cooldown = 80;
            if (willCombo && adx < 1.7f) { StartAttack("E_SWORD_B"); return; }
            retreatFrames = 30; // 收招后撤一步
            return;
        }

        if (retreatFrames > 0)
        {
            retreatFrames--;
            actor.inp.moveX = -dir * 0.5f;
            return;
        }

        if (cooldown <= 0)
        {
            if (adx <= 1.4f)
            {
                comboStep = 1;
                willCombo = Random.value < 0.65f;
                StartAttack("E_SWORD_A");
                return;
            }
            if (adx > 2.2f && adx < 5.5f && Random.value < 0.02f)
            {
                cooldown = 150;
                StartAttack("E_SWORD_DASH");
                return;
            }
        }

        if (adx > 1.2f) actor.inp.moveX = dir;
    }
}

/// <summary>
/// 精英捕头（红甲）：三连斩（第三下红甲霸体）、红甲冲刺（弹反教学）、砸地。
/// 半血后攻势更密。
/// </summary>
public class CaptainBrain : EnemyBrain
{
    public override void Think()
    {
        if (actor.dead) return;
        actor.inp.moveX = 0f;
        if (cooldown > 0) cooldown--;

        CombatActor player = FindPlayer();
        if (player == null) return;
        if (Busy) return;

        bool enraged = actor.hp < actor.maxHP * 0.5f;
        float dx = player.FeetPos.x - actor.FeetPos.x;
        float adx = Mathf.Abs(dx);
        int dir = dx >= 0f ? 1 : -1;

        if (!(actor.state is GroundedState)) return;
        actor.facing = dir;

        // 三连斩续段
        if (comboStep > 0)
        {
            if (adx < 2.2f)
            {
                if (comboStep == 1) { comboStep = 2; StartAttack("E_CAPT_2"); return; }
                if (comboStep == 2) { comboStep = 3; StartAttack("E_CAPT_3"); return; }
            }
            comboStep = 0;
            cooldown = enraged ? 70 : 110;
            return;
        }

        if (cooldown <= 0)
        {
            if (adx <= 1.7f)
            {
                if (Random.value < 0.25f) { cooldown = enraged ? 80 : 120; StartAttack("E_CAPT_SLAM"); return; }
                comboStep = 1;
                StartAttack("E_CAPT_1");
                return;
            }
            if (adx > 2.5f && adx < 7.5f)
            {
                cooldown = enraged ? 100 : 160;
                StartAttack("E_CAPT_CHARGE");
                return;
            }
        }

        if (adx > 1.5f) actor.inp.moveX = dir * (cooldown > 0 ? 0.5f : 1f);
    }
}
