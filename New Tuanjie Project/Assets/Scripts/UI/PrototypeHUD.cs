using UnityEngine;
using UnityEngine.SceneManagement;

/// <summary>
/// 原型 HUD（OnGUI）：气血/内力/剑意、敌人头顶血条架势条、浮字消息、键位提示、败北画面。
/// </summary>
public class PrototypeHUD : MonoBehaviour
{
    public CombatActor player;

    GUIStyle label, big, small;
    Texture2D white;
    Font font;
    bool styleReady;
    float deathTimer;

    void EnsureStyle()
    {
        if (styleReady) return;
        styleReady = true;
        white = Texture2D.whiteTexture;
        string[] prefer = { "Microsoft YaHei", "SimHei", "PingFang SC", "Arial" };
        string[] installed = Font.GetOSInstalledFontNames();
        string pick = null;
        for (int i = 0; i < prefer.Length && pick == null; i++)
            for (int j = 0; j < installed.Length; j++)
                if (installed[j].IndexOf(prefer[i], System.StringComparison.OrdinalIgnoreCase) >= 0) { pick = installed[j]; break; }
        if (pick != null) font = Font.CreateDynamicFontFromOSFont(pick, 16);

        label = new GUIStyle { fontSize = 14, normal = { textColor = Color.white } };
        big = new GUIStyle { fontSize = 34, alignment = TextAnchor.MiddleCenter, normal = { textColor = Color.white } };
        small = new GUIStyle { fontSize = 12, normal = { textColor = new Color(0.8f, 0.8f, 0.8f) } };
        if (font != null) { label.font = font; big.font = font; small.font = font; }
    }

    void Update()
    {
        if (Input.GetKeyDown(KeyCode.R)) { Time.timeScale = 1f; SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex); }
        if (Input.GetKeyDown(KeyCode.Escape)) Application.Quit();
        if (CombatDirector.PlayerDead) deathTimer += Time.deltaTime;
        if (deathTimer > 2.5f) { Time.timeScale = 1f; SceneManager.LoadScene(SceneManager.GetActiveScene().buildIndex); }
    }

    void Bar(float x, float y, float w, float h, float fill, Color bg, Color fg)
    {
        GUI.color = bg; GUI.DrawTexture(new Rect(x, y, w, h), white);
        GUI.color = fg; GUI.DrawTexture(new Rect(x, y, w * Mathf.Clamp01(fill), h), white);
        GUI.color = Color.white;
    }

    void OnGUI()
    {
        EnsureStyle();
        float k = Screen.height / 1080f;

        // ---- 玩家面板（左上）----
        if (player != null)
        {
            float x = 24 * k, y = 20 * k;
            GUI.Label(new Rect(x, y, 300 * k, 24 * k), "青锋剑派 · 战斗原型", label);
            y += 26 * k;
            Bar(x, y, 300 * k, 18 * k, player.hp / player.maxHP, new Color(0.25f, 0.1f, 0.1f), new Color(0.85f, 0.25f, 0.2f));
            GUI.Label(new Rect(x + 306 * k, y - 2 * k, 120 * k, 22 * k), "气血 " + Mathf.CeilToInt(player.hp), small);
            y += 24 * k;
            Bar(x, y, 240 * k, 12 * k, player.chi / player.maxChi, new Color(0.08f, 0.15f, 0.2f), new Color(0.3f, 0.75f, 0.9f));
            GUI.Label(new Rect(x + 246 * k, y - 4 * k, 120 * k, 22 * k), "内力 " + Mathf.CeilToInt(player.chi), small);
            y += 22 * k;
            // 剑意五格
            for (int i = 0; i < 5; i++)
            {
                Color c = i < player.intent
                    ? (player.bloomArmed ? new Color(1f, 0.85f, 0.3f) : new Color(0.6f, 0.95f, 1f))
                    : new Color(0.2f, 0.2f, 0.25f);
                Bar(x + i * 30 * k, y, 24 * k, 14 * k, 1f, new Color(0.1f, 0.1f, 0.12f), c);
            }
            GUI.Label(new Rect(x + 160 * k, y - 4 * k, 140 * k, 22 * k), "剑意" + (player.bloomArmed ? "·绽放" : ""), small);
        }

        // ---- 键位（左下）----
        GUI.Label(new Rect(24 * k, Screen.height - 30 * k, 900 * k, 24 * k),
            "A/D移动  Space闪避  W+Space轻功  J轻  K重  F格挡/弹反  Shift冲刺  U破空刺  I一剑霜寒(蓄)  R重置", small);

        // ---- 敌人头顶条 ----
        var cam = Camera.main;
        if (cam != null)
        {
            var all = CombatDirector.Actors;
            for (int i = 0; i < all.Count; i++)
            {
                CombatActor e = all[i];
                if (e.isPlayer || e.dead) continue;
                Vector3 sp = cam.WorldToScreenPoint(e.FeetPos + new Vector2(0f, 1.9f));
                if (sp.z < 0) continue;
                float ex = sp.x - 35 * k, ey = Screen.height - sp.y;
                Bar(ex, ey, 70 * k, 7 * k, e.hp / e.maxHP, new Color(0.15f, 0.1f, 0.1f), new Color(0.8f, 0.2f, 0.15f));
                if (e.maxPoise > 0f)
                    Bar(ex, ey + 9 * k, 70 * k, 4 * k, e.poise / e.maxPoise, new Color(0.12f, 0.1f, 0.05f), new Color(0.9f, 0.75f, 0.25f));
                GUI.Label(new Rect(ex - 10 * k, ey - 20 * k, 120 * k, 20 * k), e.displayName, small);
            }

            // ---- 浮字 ----
            var msgs = CombatDirector.Messages;
            for (int i = 0; i < msgs.Count; i++)
            {
                var m = msgs[i];
                Vector3 sp = cam.WorldToScreenPoint(m.worldPos);
                if (sp.z < 0) continue;
                GUIStyle st = m.text.Length <= 3 ? big : label;
                Color oc = GUI.color;
                GUI.color = m.color;
                GUI.Label(new Rect(sp.x - 100 * k, Screen.height - sp.y - 10 * k, 200 * k, 40 * k), m.text, st);
                GUI.color = oc;
            }
        }

        // ---- 败北 ----
        if (CombatDirector.PlayerDead)
        {
            GUI.color = new Color(0f, 0f, 0f, 0.55f);
            GUI.DrawTexture(new Rect(0, 0, Screen.width, Screen.height), white);
            GUI.color = Color.white;
            GUI.Label(new Rect(0, Screen.height * 0.42f, Screen.width, 60 * k), "刀 落", big);
            GUI.Label(new Rect(0, Screen.height * 0.42f + 50 * k, Screen.width, 30 * k), "按 R 回到检查点", label);
        }
    }
}
