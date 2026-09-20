using UnityEngine;

/// <summary>
/// 原型引导：固定 60FPS 逻辑帧，搭建灰盒场地、相机、战斗指挥、玩家与敌人。
/// 场景里只需一个挂本脚本的空物体 + 一台相机。
/// </summary>
public class GameBootstrap : MonoBehaviour
{
    void Awake()
    {
        Application.targetFrameRate = 120;
        Time.fixedDeltaTime = 1f / 60f;
        Physics2D.gravity = new Vector2(0f, -9.81f); // 角色不走物理，仅占位

        MoveDatabase.Load();

        // 指挥
        GameObject directorGo = new GameObject("CombatDirector");
        directorGo.AddComponent<CombatDirector>();

        // 相机
        Camera cam = Camera.main;
        if (cam != null)
        {
            cam.orthographic = true;
            cam.orthographicSize = 5.5f;
            cam.backgroundColor = new Color(0.09f, 0.1f, 0.13f);
            cam.clearFlags = CameraClearFlags.SolidColor;
        }

        BuildArena();

        // 玩家：青锋剑客
        CombatActor player = CreateFighter("青锋剑客", true, new Vector2(-10f, 0.1f),
            new Color(0.88f, 0.93f, 0.95f), new Color(0.35f, 0.8f, 0.9f));
        player.maxHP = 100f; player.hp = 100f;
        player.maxChi = 100f; player.chi = 60f;
        player.runSpeed = 5.5f;
        PlayerBrain.Attach(player);

        // 杂兵刀手 ×2
        CombatActor s1 = CreateFighter("杂兵刀手", false, new Vector2(-2f, 0.1f),
            new Color(0.45f, 0.32f, 0.26f), new Color(0.7f, 0.3f, 0.2f));
        s1.maxHP = 36f; s1.hp = 36f; s1.maxPoise = 30f; s1.poise = 30f; s1.runSpeed = 3.2f;
        s1.brain = new SwordsmanBrain { actor = s1 };

        CombatActor s2 = CreateFighter("杂兵刀手", false, new Vector2(3f, 0.1f),
            new Color(0.45f, 0.32f, 0.26f), new Color(0.7f, 0.3f, 0.2f));
        s2.maxHP = 36f; s2.hp = 36f; s2.maxPoise = 30f; s2.poise = 30f; s2.runSpeed = 3.2f;
        s2.brain = new SwordsmanBrain { actor = s2 };

        // 精英捕头（红甲）
        CombatActor cap = CreateFighter("精英捕头", false, new Vector2(11f, 0.1f),
            new Color(0.35f, 0.2f, 0.2f), new Color(0.9f, 0.25f, 0.15f));
        cap.maxHP = 150f; cap.hp = 150f; cap.maxPoise = 100f; cap.poise = 100f; cap.runSpeed = 3.6f;
        cap.brain = new CaptainBrain { actor = cap };

        // 镜头
        if (cam != null)
        {
            SimpleCameraFollow follow = cam.GetComponent<SimpleCameraFollow>();
            if (follow == null) follow = cam.gameObject.AddComponent<SimpleCameraFollow>();
            follow.target = player.transform;
        }

        // HUD
        GameObject hudGo = new GameObject("HUD");
        PrototypeHUD hud = hudGo.AddComponent<PrototypeHUD>();
        hud.player = player;
    }

    CombatActor CreateFighter(string name, bool isPlayer, Vector2 spawn, Color bodyColor, Color trim)
    {
        GameObject go = new GameObject(name);
        CombatActor a = go.AddComponent<CombatActor>();
        a.isPlayer = isPlayer;
        a.Init(name, isPlayer, spawn, bodyColor, trim);
        CombatDirector.Register(a);
        return a;
    }

    void BuildArena()
    {
        // 地面（顶面 y=0）
        MakeSolid("Ground", new Vector2(0f, -0.5f), new Vector2(60f, 1f), new Color(0.22f, 0.24f, 0.28f));
        // 左右界墙
        MakeSolid("WallL", new Vector2(-19.5f, 3f), new Vector2(1f, 7f), new Color(0.18f, 0.19f, 0.22f));
        MakeSolid("WallR", new Vector2(19.5f, 3f), new Vector2(1f, 7f), new Color(0.18f, 0.19f, 0.22f));
        // 平台（轻功落点）
        MakeSolid("PlatformA", new Vector2(-6f, 2.2f), new Vector2(3.5f, 0.35f), new Color(0.26f, 0.28f, 0.33f));
        MakeSolid("PlatformB", new Vector2(5f, 2.8f), new Vector2(3.5f, 0.35f), new Color(0.26f, 0.28f, 0.33f));
    }

    void MakeSolid(string name, Vector2 center, Vector2 size, Color color)
    {
        GameObject go = SpriteFactory.CreateBox(null, name, size, color, 0);
        go.transform.position = new Vector3(center.x, center.y, 0f);
        go.layer = 6; // Ground
        BoxCollider2D col = go.AddComponent<BoxCollider2D>();
        col.size = Vector2.one; // 缩放已体现在 transform
    }
}
