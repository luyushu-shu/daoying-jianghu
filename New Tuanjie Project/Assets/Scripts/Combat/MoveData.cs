using System.Collections.Generic;
using System.Globalization;
using UnityEngine;

/// <summary>
/// 一招的帧数据。字段与 Resources/FrameData/moves.csv 一一对应。
/// 帧数以 60FPS 计（1f ≈ 16.67ms），对齐《战斗帧数据表 v0.1》。
/// </summary>
public class MoveData
{
    public string id;
    public string school;
    public string moveName;
    public int startup;        // 前摇：输入受理到首段判定
    public int active;         // 判定帧数
    public int recovery;       // 后摇
    public int cancelStart;    // 取消窗起（相对本招第0帧，0=无窗）
    public int cancelEnd;      // 取消窗止
    public string cancelTo;    // 可取消目标：L轻 H重 D闪 S技 J跳
    public float damage;       // 伤害系数（轻1=1.0）
    public float poise;        // 架势削减
    public int hitstun;        // 命中给敌硬直帧
    public int ifStart, ifEnd; // 无敌帧区间（含端点）
    public int chi;            // 内力消耗
    public float reach;        // 判定盒中心前伸（身=1.4单位已在录入时折算）
    public float boxW, boxH;   // 判定盒尺寸
    public float lunge;        // 前冲位移（单位）
    public int hitstop;        // 命中停顿帧（双方）
    public int armorFrom, armorTo; // 霸体帧区间（0=无）
    public int active2Start, active2End; // 第二段判定窗（0=无）
    public string tags;
    public string notes;

    public int Total { get { return startup + active + recovery; } }

    public bool HasTag(string t)
    {
        if (string.IsNullOrEmpty(tags)) return false;
        string[] parts = tags.Split(' ');
        for (int i = 0; i < parts.Length; i++) if (parts[i] == t) return true;
        return false;
    }

    public bool CanCancelTo(char c)
    {
        return !string.IsNullOrEmpty(cancelTo) && cancelTo.IndexOf(c) >= 0;
    }

    public bool InCancelWindow(int frame)
    {
        return cancelStart > 0 && frame >= cancelStart && frame <= cancelEnd;
    }
}

/// <summary>运行时从 CSV 构建的帧数据表。改表即改手感，无需动代码。</summary>
public static class MoveDatabase
{
    static Dictionary<string, MoveData> map;
    static bool loaded;

    public static void Load()
    {
        map = new Dictionary<string, MoveData>();
        TextAsset ta = Resources.Load<TextAsset>("FrameData/moves");
        if (ta == null) { Debug.LogError("[MoveDatabase] 未找到 Resources/FrameData/moves.csv"); loaded = true; return; }
        string[] lines = ta.text.Split('\n');
        for (int i = 1; i < lines.Length; i++)
        {
            string line = lines[i].Trim();
            if (line.Length == 0) continue;
            string[] c = line.Split(',');
            if (c.Length < 25) { Debug.LogWarning("[MoveDatabase] 跳过列数不足的行 " + i + ": " + line); continue; }
            MoveData m = new MoveData();
            m.id = c[0].Trim(); m.school = c[1].Trim(); m.moveName = c[2].Trim();
            m.startup = I(c[3]); m.active = I(c[4]); m.recovery = I(c[5]);
            m.cancelStart = I(c[6]); m.cancelEnd = I(c[7]); m.cancelTo = c[8].Trim();
            m.damage = F(c[9]); m.poise = F(c[10]); m.hitstun = I(c[11]);
            m.ifStart = I(c[12]); m.ifEnd = I(c[13]); m.chi = I(c[14]);
            m.reach = F(c[15]); m.boxW = F(c[16]); m.boxH = F(c[17]); m.lunge = F(c[18]);
            m.hitstop = I(c[19]); m.armorFrom = I(c[20]); m.armorTo = I(c[21]);
            m.active2Start = I(c[22]); m.active2End = I(c[23]);
            m.tags = c[24].Trim();
            m.notes = c.Length > 25 ? c[25].Trim() : "";
            map[m.id] = m;
        }
        loaded = true;
        Debug.Log("[MoveDatabase] 载入招式 " + map.Count + " 条");
    }

    static int I(string s) { int v; if (int.TryParse(s.Trim(), NumberStyles.Integer, CultureInfo.InvariantCulture, out v)) return v; return 0; }
    static float F(string s) { float v; if (float.TryParse(s.Trim(), NumberStyles.Float, CultureInfo.InvariantCulture, out v)) return v; return 0f; }

    public static MoveData Get(string id)
    {
        if (!loaded) Load();
        MoveData m;
        if (map != null && map.TryGetValue(id, out m)) return m;
        Debug.LogWarning("[MoveDatabase] 未找到招式 " + id);
        return null;
    }
}

/// <summary>一次命中的结算信息。</summary>
public struct HitInfo
{
    public float damage;
    public float poise;
    public int hitstun;
    public int hitstop;
    public bool unblockable;
    public CombatActor attacker;
    public string moveId;

    public static HitInfo From(MoveData mv, CombatActor attacker, float dmgScale, float poiseScale)
    {
        HitInfo h;
        h.damage = mv.damage * dmgScale;
        h.poise = mv.poise * poiseScale;
        h.hitstun = mv.hitstun;
        h.hitstop = mv.hitstop;
        h.unblockable = mv.HasTag("unblockable");
        h.attacker = attacker;
        h.moveId = mv.id;
        return h;
    }
}
