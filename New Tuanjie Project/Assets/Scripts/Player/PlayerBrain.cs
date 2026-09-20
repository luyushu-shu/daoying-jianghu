using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// 玩家脑：Update 里捕获按键进 6 帧输入缓冲，FixedUpdate 由角色调用 Think 倒入意图。
/// 键位对齐 GDD §3.1：A/D移动 Space闪避 W+Space轻功 J轻 K重 F格挡 Shift冲刺 U/I技能。
/// </summary>
public class PlayerBrain : Brain
{
    class Entry { public string action; public int expireFrame; }
    readonly List<Entry> buffer = new List<Entry>();
    const int BufferFrames = 6;

    public static PlayerBrain Attach(CombatActor actor)
    {
        PlayerBrainBehaviour b = actor.gameObject.AddComponent<PlayerBrainBehaviour>();
        b.Init(actor);
        return b.Brain;
    }

    public void Buffer(string action)
    {
        buffer.Add(new Entry { action = action, expireFrame = CombatDirector.Frame + BufferFrames });
    }

    /// <summary>状态消费意图后移除最早一条缓冲，防止同一按键重复触发。</summary>
    public void ConsumeAction(string action)
    {
        for (int i = 0; i < buffer.Count; i++)
        {
            if (buffer[i].action == action) { buffer.RemoveAt(i); return; }
        }
    }

    public override void Think()
    {
        // 持续意图
        float mx = 0f;
        if (Input.GetKey(KeyCode.A)) mx -= 1f;
        if (Input.GetKey(KeyCode.D)) mx += 1f;
        actor.inp.moveX = mx;
        actor.inp.blockHeld = Input.GetKey(KeyCode.F);
        actor.inp.skill2Held = Input.GetKey(KeyCode.I);

        // 缓冲的一次性意图
        for (int i = buffer.Count - 1; i >= 0; i--)
        {
            Entry e = buffer[i];
            if (CombatDirector.Frame > e.expireFrame) { buffer.RemoveAt(i); continue; }
            switch (e.action)
            {
                case "light": actor.inp.light = true; break;
                case "heavy": actor.inp.heavy = true; break;
                case "skill1": actor.inp.skill1 = true; break;
                case "skill2": actor.inp.skill2 = true; break;
                case "dodge": actor.inp.dodge = true; break;
                case "jump": actor.inp.jump = true; break;
                case "dash": actor.inp.dash = true; break;
            }
        }
    }

    /// <summary>挂在玩家物体上的输入捕获组件。</summary>
    class PlayerBrainBehaviour : MonoBehaviour
    {
        public PlayerBrain Brain { get; private set; }

        public void Init(CombatActor actor)
        {
            Brain = new PlayerBrain();
            Brain.actor = actor;
            actor.brain = Brain;
        }

        void Update()
        {
            if (CombatDirector.PlayerDead) return;
            if (Input.GetKeyDown(KeyCode.J)) Brain.Buffer("light");
            if (Input.GetKeyDown(KeyCode.K)) Brain.Buffer("heavy");
            if (Input.GetKeyDown(KeyCode.U)) Brain.Buffer("skill1");
            if (Input.GetKeyDown(KeyCode.I)) Brain.Buffer("skill2");
            if (Input.GetKeyDown(KeyCode.Space))
            {
                if (Input.GetKey(KeyCode.W)) Brain.Buffer("jump");
                else Brain.Buffer("dodge");
            }
            if (Input.GetKeyDown(KeyCode.LeftShift)) Brain.Buffer("dash");
        }
    }
}
