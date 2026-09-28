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
    const int BufferFrames = 18; // 300ms 宽松输入缓冲

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
        if (Input.GetKey(KeyCode.A) || Input.GetKey(KeyCode.LeftArrow)) mx -= 1f;
        if (Input.GetKey(KeyCode.D) || Input.GetKey(KeyCode.RightArrow)) mx += 1f;
        actor.inp.moveX = mx;
        actor.inp.blockHeld = Input.GetKey(KeyCode.F) && !Input.GetKey(KeyCode.LeftShift) && !Input.GetKey(KeyCode.RightShift);
        actor.inp.skill2Held = Input.GetKey(KeyCode.I);
        actor.inp.skill5Held = Input.GetKey(KeyCode.G) || ((Input.GetKey(KeyCode.LeftShift) || Input.GetKey(KeyCode.RightShift)) && Input.GetKey(KeyCode.F));

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
                case "skill3": actor.inp.skill3 = true; break;
                case "skill4": actor.inp.skill4 = true; break;
                case "skill5": actor.inp.skill5 = true; break;
                case "skill6": actor.inp.skill6 = true; break;
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

            // 普攻：J 键 或 鼠标左键
            if (Input.GetKeyDown(KeyCode.J) || Input.GetMouseButtonDown(0)) Brain.Buffer("light");

            // 重击：K 键 或 鼠标右键
            if (Input.GetKeyDown(KeyCode.K) || Input.GetMouseButtonDown(1)) Brain.Buffer("heavy");

            // 技能 1~6：支持 Q/E/R/T/G 以及 U/I/O/P 双模式操作
            if (Input.GetKeyDown(KeyCode.U) || Input.GetKeyDown(KeyCode.Q)) Brain.Buffer("skill1"); // 破空刺
            if (Input.GetKeyDown(KeyCode.I)) Brain.Buffer("skill2");                               // 一剑霜寒
            if (Input.GetKeyDown(KeyCode.O) || Input.GetKeyDown(KeyCode.E)) Brain.Buffer("skill3"); // 回风舞
            if (Input.GetKeyDown(KeyCode.P) || Input.GetKeyDown(KeyCode.R)) Brain.Buffer("skill4"); // 御剑飞来
            if (Input.GetKeyDown(KeyCode.G) || ((Input.GetKey(KeyCode.LeftShift) || Input.GetKey(KeyCode.RightShift)) && Input.GetKeyDown(KeyCode.F))) Brain.Buffer("skill5"); // 以剑御气
            if (Input.GetKeyDown(KeyCode.T)) Brain.Buffer("skill6");                               // 万剑归宗 (终极奥义)

            // 跳跃：W 或 向上方向键
            if (Input.GetKeyDown(KeyCode.W) || Input.GetKeyDown(KeyCode.UpArrow)) Brain.Buffer("jump");

            // 闪避与跳跃：Space 键（按住 W 时为空中轻功，单独按下为翻滚闪避）
            if (Input.GetKeyDown(KeyCode.Space))
            {
                if (Input.GetKey(KeyCode.W) || Input.GetKey(KeyCode.UpArrow)) Brain.Buffer("jump");
                else Brain.Buffer("dodge");
            }

            // 疾跑冲刺：Shift 键
            if (Input.GetKeyDown(KeyCode.LeftShift) || Input.GetKeyDown(KeyCode.RightShift)) Brain.Buffer("dash");
        }

    }
}
