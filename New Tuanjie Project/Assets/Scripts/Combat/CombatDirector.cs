using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// 战斗指挥：全局帧计数、角色注册表、打击信息、震屏、弹反时缓、浮字消息。
/// 伤害换算：系数1.0 = DamageUnit 点气血。
/// </summary>
public class CombatDirector : MonoBehaviour
{
    public const float DamageUnit = 6f;

    public static CombatDirector Instance { get; private set; }
    public static int Frame { get; private set; }

    static readonly List<CombatActor> actors = new List<CombatActor>();
    public static List<CombatActor> Actors { get { return actors; } }

    public class FloatMsg
    {
        public string text;
        public Vector3 worldPos;
        public Color color;
        public int expireFrame;
    }
    static readonly List<FloatMsg> msgs = new List<FloatMsg>();
    public static List<FloatMsg> Messages { get { return msgs; } }

    // 时缓
    float slowmoScale = 1f;
    int slowmoUntil = -1;

    // 震屏
    float shakeAmp;
    int shakeUntil = -1;
    public Vector2 ShakeOffset { get; private set; }

    public static bool PlayerDead;

    void Awake()
    {
        Instance = this;
        Frame = 0;
        actors.Clear();
        msgs.Clear();
        PlayerDead = false;
        Time.timeScale = 1f;
        Time.fixedDeltaTime = 1f / 60f;
    }

    void FixedUpdate()
    {
        Frame++;

        if (slowmoUntil > 0 && Frame > slowmoUntil)
        {
            slowmoUntil = -1;
            Time.timeScale = 1f;
            Time.fixedDeltaTime = 1f / 60f;
        }

        if (Frame <= shakeUntil)
        {
            ShakeOffset = new Vector2(Random.Range(-shakeAmp, shakeAmp), Random.Range(-shakeAmp, shakeAmp));
            shakeAmp *= 0.9f;
        }
        else ShakeOffset = Vector2.zero;

        for (int i = msgs.Count - 1; i >= 0; i--)
            if (Frame > msgs[i].expireFrame) msgs.RemoveAt(i);
    }

    void OnDestroy()
    {
        Time.timeScale = 1f;
        Time.fixedDeltaTime = 1f / 60f;
        if (Instance == this) Instance = null;
    }

    public static void Register(CombatActor a) { if (!actors.Contains(a)) actors.Add(a); }
    public static void Unregister(CombatActor a) { actors.Remove(a); }

    public static void Msg(string text, Vector2 worldPos, Color color, int frames)
    {
        msgs.Add(new FloatMsg { text = text, worldPos = worldPos, color = color, expireFrame = Frame + frames });
    }

    public static void Shake(float amp, int frames)
    {
        if (Instance == null) return;
        Instance.shakeAmp = Mathf.Max(Instance.shakeAmp, amp);
        Instance.shakeUntil = Frame + frames;
    }

    /// <summary>弹反时缓：scale=0.6 持续 frames 个游戏帧。</summary>
    public static void SlowMo(float scale, int frames)
    {
        if (Instance == null) return;
        Instance.slowmoScale = scale;
        Instance.slowmoUntil = Frame + frames;
        Time.timeScale = scale;
        Time.fixedDeltaTime = (1f / 60f) * scale;
    }

    public static void OnPlayerDeath()
    {
        PlayerDead = true;
    }
}
