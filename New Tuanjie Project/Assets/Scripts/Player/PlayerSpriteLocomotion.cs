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
    const float GuardBreakStunDuration = 1.25f; // 破防大僵直时长 (1.25秒 / 75帧)

    public Animator animator;
    public SpriteRenderer spriteRenderer;
    CombatActor combat;

    float dodgeTimer = 0f;
    float dodgeDir = 1f;
    float blockTimer = 0f;
    bool isBlockingHeld = false;
    bool isBlockingFromGui = false;
    float blockHoldDuration = 0f;
    float blockRecoveryTimer = 0f; // 松开按键后的收招动作计时 (0.24s，播放 guard-5 -> guard-6 -> guard-7)
    float guardStrain = 0f;       // 架势负荷 (0~100，爆满强制弹刀破防)
    float blockEfficiency = 1.0f; // 格挡效能 (1.0 -> 0.30 维持时间越久越弱)
    float stunTimer = 0f;         // 破防僵直计时器

    public bool IsBlocking => isBlockingHeld || blockTimer > 0f;
    public bool IsParryWindow => IsBlocking && blockHoldDuration <= ParryWindow;
    public bool IsStunned => stunTimer > 0f;
    public bool IsBlockExiting => blockRecoveryTimer > 0f;
    public float BlockEfficiency => blockEfficiency;
    public float GuardStrain => guardStrain;
    public float StunTimer => stunTimer;

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
    [SerializeField] public Sprite[] pokongciBloomSprites;
    [SerializeField] public Sprite[] huifengwuSprites;
    [SerializeField] public Sprite[] huifengwuBloomSprites;
    [SerializeField] public Sprite[] yijianshuanghanSprites;
    [SerializeField] public Sprite[] yijianshuanghanBloomSprites;
    [SerializeField] public Sprite[] yinjianjueSprites;
    [SerializeField] public Sprite[] yinjianjueBloomSprites;
    [SerializeField] public Sprite[] yijianyuqiSprites;
    [SerializeField] public Sprite[] yijianyuqiBloomSprites;
    [SerializeField] public Sprite[] wanjianSprites;
    [SerializeField] public Sprite[] wanjianBloomSprites;
    [SerializeField] public Sprite swordProjectileNormalSprite;
    [SerializeField] public Sprite swordProjectileBloomSprite;
    [SerializeField] public Sprite fallingSwordNormal45Sprite;
    [SerializeField] public Sprite fallingSwordBloom45Sprite;

    // 以剑御气 · 苍龙玄天钟 / 万仞诛魔金刚剑界 (按住维持护盾，无时间衰减，全额吸收伤害)
    public bool isYuqiShieldActive = false;
    public bool isYuqiBloomShieldActive = false;
    public float yuqiAbsorbedDamage = 0f;
    public float yuqiBloomAbsorbedDamage = 0f;
    public float maxYuqiShield = 100f;
    public float maxYuqiBloomShield = 180f;
    private bool isYuqiFromGui = false;
    public bool IsYuqiGuarding => isYuqiShieldActive || isYuqiBloomShieldActive;

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
        LoadPokongciBloomSprites();
        LoadHuifengwuSprites();
        LoadHuifengwuBloomSprites();
        LoadYijianshuanghanSprites();
        LoadYijianshuanghanBloomSprites();
        LoadYinjianjueSprites();
        LoadYinjianjueBloomSprites();
        LoadYijianyuqiSprites();
        LoadYijianyuqiBloomSprites();
        LoadWanjianSprites();
        LoadWanjianBloomSprites();
        LoadWanjianProjectiles();
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

    public void LoadYijianshuanghanBloomSprites()
    {
#if UNITY_EDITOR
        List<Sprite> list = new List<Sprite>();
        for (int i = 1; i <= 8; i++)
        {
            string p = $"Assets/Sprites/Player/Skills/Yijianshuanghan_Bloom/yijianshuanghan-bloom-{i}.png";
            Sprite sp = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>(p);
            if (sp != null) list.Add(sp);
        }
        if (list.Count >= 8)
        {
            yijianshuanghanBloomSprites = list.ToArray();
            return;
        }
#endif
        LoadYijianshuanghanBloomSpritesFromDisk();
    }

    void LoadYijianshuanghanBloomSpritesFromDisk()
    {
        string dir = System.IO.Path.Combine(Application.dataPath, "Sprites/Player/Skills/Yijianshuanghan_Bloom");
        List<Sprite> list = new List<Sprite>();
        for (int i = 1; i <= 8; i++)
        {
            string filePath = System.IO.Path.Combine(dir, $"yijianshuanghan-bloom-{i}.png");
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
            yijianshuanghanBloomSprites = list.ToArray();
            Debug.Log($"[PlayerSpriteLocomotion] Successfully loaded {yijianshuanghanBloomSprites.Length} Yijianshuanghan Bloom sprites directly from disk!");
        }
        else
        {
            Debug.LogWarning($"[PlayerSpriteLocomotion] Failed to load 8 Yijianshuanghan Bloom sprites from disk (loaded {list.Count}) at {dir}");
        }
    }

    public void LoadYinjianjueSprites()
    {
#if UNITY_EDITOR
        List<Sprite> list = new List<Sprite>();
        for (int i = 1; i <= 8; i++)
        {
            string p = $"Assets/Sprites/Player/Skills/Yinjianjue/yinjianjue-{i}.png";
            Sprite sp = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>(p);
            if (sp != null) list.Add(sp);
        }
        if (list.Count >= 8)
        {
            yinjianjueSprites = list.ToArray();
            return;
        }
#endif
        LoadYinjianjueSpritesFromDisk();
    }

    void LoadYinjianjueSpritesFromDisk()
    {
        string dir = System.IO.Path.Combine(Application.dataPath, "Sprites/Player/Skills/Yinjianjue");
        List<Sprite> list = new List<Sprite>();
        for (int i = 1; i <= 8; i++)
        {
            string filePath = System.IO.Path.Combine(dir, $"yinjianjue-{i}.png");
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
            yinjianjueSprites = list.ToArray();
            Debug.Log($"[PlayerSpriteLocomotion] Successfully loaded {yinjianjueSprites.Length} Yinjianjue sprites directly from disk!");
        }
        else
        {
            Debug.LogWarning($"[PlayerSpriteLocomotion] Failed to load 8 Yinjianjue sprites from disk (loaded {list.Count}) at {dir}");
        }
    }

    public void LoadYinjianjueBloomSprites()
    {
#if UNITY_EDITOR
        List<Sprite> list = new List<Sprite>();
        for (int i = 1; i <= 8; i++)
        {
            string p = $"Assets/Sprites/Player/Skills/Yinjianjue_Bloom/yinjianjue-bloom-{i}.png";
            Sprite sp = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>(p);
            if (sp != null) list.Add(sp);
        }
        if (list.Count >= 8)
        {
            yinjianjueBloomSprites = list.ToArray();
            return;
        }
#endif
        LoadYinjianjueBloomSpritesFromDisk();
    }

    void LoadYinjianjueBloomSpritesFromDisk()
    {
        string dir = System.IO.Path.Combine(Application.dataPath, "Sprites/Player/Skills/Yinjianjue_Bloom");
        List<Sprite> list = new List<Sprite>();
        for (int i = 1; i <= 8; i++)
        {
            string filePath = System.IO.Path.Combine(dir, $"yinjianjue-bloom-{i}.png");
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
            yinjianjueBloomSprites = list.ToArray();
            Debug.Log($"[PlayerSpriteLocomotion] Successfully loaded {yinjianjueBloomSprites.Length} Yinjianjue Bloom sprites directly from disk!");
        }
        else
        {
            Debug.LogWarning($"[PlayerSpriteLocomotion] Failed to load 8 Yinjianjue Bloom sprites from disk (loaded {list.Count}) at {dir}");
        }
    }

    public void LoadYijianyuqiSprites()
    {
#if UNITY_EDITOR
        List<Sprite> list = new List<Sprite>();
        for (int i = 1; i <= 16; i++)
        {
            string p = $"Assets/Sprites/Player/Skills/Yijianyuqi/yijianyuqi-{i}.png";
            Sprite sp = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>(p);
            if (sp != null) list.Add(sp);
        }
        if (list.Count >= 16)
        {
            yijianyuqiSprites = list.ToArray();
            return;
        }
#endif
        LoadYijianyuqiSpritesFromDisk();
    }

    void LoadYijianyuqiSpritesFromDisk()
    {
        string dir = System.IO.Path.Combine(Application.dataPath, "Sprites/Player/Skills/Yijianyuqi");
        List<Sprite> list = new List<Sprite>();
        for (int i = 1; i <= 16; i++)
        {
            string filePath = System.IO.Path.Combine(dir, $"yijianyuqi-{i}.png");
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
        if (list.Count >= 16)
        {
            yijianyuqiSprites = list.ToArray();
            Debug.Log($"[PlayerSpriteLocomotion] Successfully loaded {yijianyuqiSprites.Length} Yijianyuqi sprites directly from disk!");
        }
        else
        {
            Debug.LogWarning($"[PlayerSpriteLocomotion] Failed to load 16 Yijianyuqi sprites from disk (loaded {list.Count}) at {dir}");
        }
    }

    public void LoadYijianyuqiBloomSprites()
    {
#if UNITY_EDITOR
        List<Sprite> list = new List<Sprite>();
        for (int i = 1; i <= 16; i++)
        {
            string p = $"Assets/Sprites/Player/Skills/Yijianyuqi_Bloom/yijianyuqi-bloom-{i}.png";
            Sprite sp = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>(p);
            if (sp != null) list.Add(sp);
        }
        if (list.Count >= 16)
        {
            yijianyuqiBloomSprites = list.ToArray();
            return;
        }
#endif
        LoadYijianyuqiBloomSpritesFromDisk();
    }

    void LoadYijianyuqiBloomSpritesFromDisk()
    {
        string dir = System.IO.Path.Combine(Application.dataPath, "Sprites/Player/Skills/Yijianyuqi_Bloom");
        List<Sprite> list = new List<Sprite>();
        for (int i = 1; i <= 16; i++)
        {
            string filePath = System.IO.Path.Combine(dir, $"yijianyuqi-bloom-{i}.png");
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
        if (list.Count >= 16)
        {
            yijianyuqiBloomSprites = list.ToArray();
            Debug.Log($"[PlayerSpriteLocomotion] Successfully loaded {yijianyuqiBloomSprites.Length} Yijianyuqi Bloom sprites directly from disk!");
        }
        else
        {
            Debug.LogWarning($"[PlayerSpriteLocomotion] Failed to load 16 Yijianyuqi Bloom sprites from disk (loaded {list.Count}) at {dir}");
        }
    }

    public void LoadWanjianSprites()
    {
#if UNITY_EDITOR
        List<Sprite> list = new List<Sprite>();
        for (int i = 1; i <= 16; i++)
        {
            string p = $"Assets/Sprites/Player/Skills/Wanjian/wanjian-{i}.png";
            Sprite sp = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>(p);
            if (sp != null) list.Add(sp);
        }
        if (list.Count >= 16)
        {
            wanjianSprites = list.ToArray();
            return;
        }
#endif
        LoadWanjianSpritesFromDisk();
    }

    void LoadWanjianSpritesFromDisk()
    {
        string dir = System.IO.Path.Combine(Application.dataPath, "Sprites/Player/Skills/Wanjian");
        List<Sprite> list = new List<Sprite>();
        for (int i = 1; i <= 16; i++)
        {
            string filePath = System.IO.Path.Combine(dir, $"wanjian-{i}.png");
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
        if (list.Count >= 16)
        {
            wanjianSprites = list.ToArray();
            Debug.Log($"[PlayerSpriteLocomotion] Successfully loaded {wanjianSprites.Length} Wanjian sprites directly from disk!");
        }
        else
        {
            Debug.LogWarning($"[PlayerSpriteLocomotion] Failed to load 16 Wanjian sprites from disk (loaded {list.Count}) at {dir}");
        }
    }

    public void LoadWanjianBloomSprites()
    {
#if UNITY_EDITOR
        List<Sprite> list = new List<Sprite>();
        for (int i = 1; i <= 16; i++)
        {
            string p = $"Assets/Sprites/Player/Skills/Wanjian_Bloom/wanjian-bloom-{i}.png";
            Sprite sp = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>(p);
            if (sp != null) list.Add(sp);
        }
        if (list.Count >= 16)
        {
            wanjianBloomSprites = list.ToArray();
            return;
        }
#endif
        LoadWanjianBloomSpritesFromDisk();
    }

    void LoadWanjianBloomSpritesFromDisk()
    {
        string dir = System.IO.Path.Combine(Application.dataPath, "Sprites/Player/Skills/Wanjian_Bloom");
        List<Sprite> list = new List<Sprite>();
        for (int i = 1; i <= 16; i++)
        {
            string filePath = System.IO.Path.Combine(dir, $"wanjian-bloom-{i}.png");
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
        if (list.Count >= 16)
        {
            wanjianBloomSprites = list.ToArray();
            Debug.Log($"[PlayerSpriteLocomotion] Successfully loaded {wanjianBloomSprites.Length} Wanjian Bloom sprites directly from disk!");
        }
        else
        {
            Debug.LogWarning($"[PlayerSpriteLocomotion] Failed to load 16 Wanjian Bloom sprites from disk (loaded {list.Count}) at {dir}");
        }
    }

    public void LoadWanjianProjectiles()
    {
#if UNITY_EDITOR
        swordProjectileNormalSprite = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Sprites/Player/Skills/Wanjian/sword_projectile_normal_clean.png");
        fallingSwordNormal45Sprite = swordProjectileNormalSprite;
        swordProjectileBloomSprite = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Sprites/Player/Skills/Wanjian_Bloom/sword_projectile_bloom_clean.png");
        fallingSwordBloom45Sprite = swordProjectileBloomSprite;
        if (fallingSwordNormal45Sprite != null && fallingSwordBloom45Sprite != null) return;
#endif
        string dirWanjian = System.IO.Path.Combine(Application.dataPath, "Sprites/Player/Skills/Wanjian");
        string pNorm = System.IO.Path.Combine(dirWanjian, "sword_projectile_normal_clean.png");
        if (System.IO.File.Exists(pNorm))
        {
            byte[] b = System.IO.File.ReadAllBytes(pNorm);
            Texture2D t = new Texture2D(2, 2);
            if (t.LoadImage(b))
            {
                fallingSwordNormal45Sprite = Sprite.Create(t, new Rect(0, 0, t.width, t.height), new Vector2(0.5f, 0.5f), 214f);
                swordProjectileNormalSprite = fallingSwordNormal45Sprite;
            }
        }
        string dirBloom = System.IO.Path.Combine(Application.dataPath, "Sprites/Player/Skills/Wanjian_Bloom");
        string pBloom = System.IO.Path.Combine(dirBloom, "sword_projectile_bloom_clean.png");
        if (System.IO.File.Exists(pBloom))
        {
            byte[] b = System.IO.File.ReadAllBytes(pBloom);
            Texture2D t = new Texture2D(2, 2);
            if (t.LoadImage(b))
            {
                fallingSwordBloom45Sprite = Sprite.Create(t, new Rect(0, 0, t.width, t.height), new Vector2(0.5f, 0.5f), 214f);
                swordProjectileBloomSprite = fallingSwordBloom45Sprite;
            }
        }
    }

    public void LoadPokongciSprites()
    {
#if UNITY_EDITOR
        List<Sprite> list = new List<Sprite>();
        for (int i = 1; i <= 8; i++)
        {
            string p = $"Assets/Sprites/Player/Skills/Pokongci/pokongci-{i}.png";
            Sprite sp = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>(p);
            if (sp != null) list.Add(sp);
        }
        if (list.Count >= 8)
        {
            pokongciSprites = list.ToArray();
            return;
        }
#endif
        LoadPokongciSpritesFromDisk();
    }

    void LoadPokongciSpritesFromDisk()
    {
        string dir = System.IO.Path.Combine(Application.dataPath, "Sprites/Player/Skills/Pokongci");
        List<Sprite> list = new List<Sprite>();
        for (int i = 1; i <= 8; i++)
        {
            string filePath = System.IO.Path.Combine(dir, $"pokongci-{i}.png");
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
            pokongciSprites = list.ToArray();
            Debug.Log($"[PlayerSpriteLocomotion] Successfully loaded {pokongciSprites.Length} Pokongci sprites directly from disk!");
        }
        else
        {
            Debug.LogWarning($"[PlayerSpriteLocomotion] Failed to load 8 Pokongci sprites from disk (loaded {list.Count}) at {dir}");
        }
    }

    public void LoadPokongciBloomSprites()
    {
#if UNITY_EDITOR
        List<Sprite> list = new List<Sprite>();
        for (int i = 1; i <= 8; i++)
        {
            string p = $"Assets/Sprites/Player/Skills/Pokongci_Bloom/pokongci-bloom-{i}.png";
            Sprite sp = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>(p);
            if (sp != null) list.Add(sp);
        }
        if (list.Count >= 8)
        {
            pokongciBloomSprites = list.ToArray();
            return;
        }
#endif
        LoadPokongciBloomSpritesFromDisk();
    }

    void LoadPokongciBloomSpritesFromDisk()
    {
        string dir = System.IO.Path.Combine(Application.dataPath, "Sprites/Player/Skills/Pokongci_Bloom");
        List<Sprite> list = new List<Sprite>();
        for (int i = 1; i <= 8; i++)
        {
            string filePath = System.IO.Path.Combine(dir, $"pokongci-bloom-{i}.png");
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
            pokongciBloomSprites = list.ToArray();
            Debug.Log($"[PlayerSpriteLocomotion] Successfully loaded {pokongciBloomSprites.Length} Pokongci Bloom sprites directly from disk!");
        }
        else
        {
            Debug.LogWarning($"[PlayerSpriteLocomotion] Failed to load 8 Pokongci Bloom sprites from disk (loaded {list.Count}) at {dir}");
        }
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

    public void LoadHuifengwuBloomSprites()
    {
#if UNITY_EDITOR
        List<Sprite> list = new List<Sprite>();
        for (int i = 1; i <= 8; i++)
        {
            string p = $"Assets/Sprites/Player/Skills/Huifengwu_Bloom/huifengwu-bloom-{i}.png";
            Sprite sp = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>(p);
            if (sp != null) list.Add(sp);
        }
        if (list.Count >= 8)
        {
            huifengwuBloomSprites = list.ToArray();
            return;
        }
#endif
        LoadHuifengwuBloomSpritesFromDisk();
    }

    void LoadHuifengwuBloomSpritesFromDisk()
    {
        string dir = System.IO.Path.Combine(Application.dataPath, "Sprites/Player/Skills/Huifengwu_Bloom");
        List<Sprite> list = new List<Sprite>();
        for (int i = 1; i <= 8; i++)
        {
            string filePath = System.IO.Path.Combine(dir, $"huifengwu-bloom-{i}.png");
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
            huifengwuBloomSprites = list.ToArray();
            Debug.Log($"[PlayerSpriteLocomotion] Successfully loaded {huifengwuBloomSprites.Length} Huifengwu Bloom sprites directly from disk!");
        }
        else
        {
            Debug.LogWarning($"[PlayerSpriteLocomotion] Failed to load 8 Huifengwu Bloom sprites from disk (loaded {list.Count}) at {dir}");
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

        // 破防僵直状态（弹刀后陷入硬直，无法行动）
        if (stunTimer > 0f)
        {
            stunTimer -= Time.deltaTime;
            currentActionName = $"【弹刀破防僵直】无法行动 ({stunTimer:F1}s)";
            // 僵直期间微红受损受击闪烁
            if (spriteRenderer != null)
            {
                float pulse = Mathf.PingPong(Time.time * 6f, 0.35f);
                spriteRenderer.color = new Color(1f, 0.65f - pulse, 0.65f - pulse, 1f);
            }
            // 恢复架势负荷
            guardStrain = Mathf.Lerp(guardStrain, 0f, Time.deltaTime * 3f);
            if (stunTimer <= 0f)
            {
                stunTimer = 0f;
                guardStrain = 0f;
                if (spriteRenderer != null) spriteRenderer.color = Color.white;
                currentActionName = "待机 (Idle)";
                if (animator != null)
                {
                    animator.Play("Idle", 0, 0f);
                }
            }
            return; // 僵直期间完全屏蔽所有移动、攻击、格挡、闪避输入
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

        // 格挡架势持续更新与衰减
        if (isBlockingHeld || blockTimer > 0f)
        {
            // 维持按住按键：格挡持续不退；松开按键则立即开始收招卸劲
            if (Input.GetKey(KeyCode.F) || isBlockingFromGui)
            {
                isBlockingHeld = true;
                blockHoldDuration += Time.deltaTime;

                // 维持时间越久，格挡效果越弱：
                // 前 0.25 秒为稳态 (100%)，随后在 3.0 秒内线性衰减至 30% 最低稳态
                float decayTime = Mathf.Max(0f, blockHoldDuration - 0.25f);
                blockEfficiency = Mathf.Clamp(1.0f - (decayTime / 3.0f) * 0.70f, 0.30f, 1.0f);

                // 长时间维持格挡消耗少量架势负荷（疲劳微增，不自爆）
                if (blockHoldDuration > 1.2f)
                {
                    guardStrain = Mathf.Min(guardStrain + Time.deltaTime * 6.5f * (1.1f - blockEfficiency), 85f);
                }

                currentActionName = $"格挡架势 (效能:{Mathf.RoundToInt(blockEfficiency * 100)}% 负荷:{Mathf.RoundToInt(guardStrain)}/100)";

                // 效能过低时身法出现轻度颤抖力竭反馈
                if (blockEfficiency < 0.65f)
                {
                    float shake = Mathf.Sin(Time.time * 50f) * 0.008f * (1f - blockEfficiency);
                    transform.position += new Vector3(shake, 0f, 0f);
                }

                // 格挡主动取消：闪避
                if (Input.GetKeyDown(KeyCode.Space))
                {
                    ExitBlock();
                    StartDodge();
                    return;
                }

                // 格挡主动取消：轻攻击
                if (Input.GetKeyDown(KeyCode.J) || Input.GetMouseButtonDown(0))
                {
                    ExitBlock();
                    PerformNextAttack();
                    return;
                }

                // 格挡主动取消：重刺
                if (Input.GetKeyDown(KeyCode.K) || Input.GetMouseButtonDown(1))
                {
                    ExitBlock();
                    PerformHeavyThrust();
                    return;
                }

                // 模拟受击 (G 或 H，累计架势负荷并在爆满时弹刀破防)
                if (Input.GetKeyDown(KeyCode.G) || Input.GetKeyDown(KeyCode.H))
                {
                    TriggerBlockHit();
                    return;
                }

                // 模拟弹反成功 (T，大幅化解架势负荷)
                if (Input.GetKeyDown(KeyCode.T))
                {
                    TriggerParrySuccess();
                    return;
                }

                return;
            }
            else
            {
                // 松开 F 键：立即退出架势并播放后续收招卸劲动作 (guard-5 -> guard-6 -> guard-7 -> Idle)
                ExitBlock();
            }
        }
        else
        {
            // 非格挡且非僵直状态下，架势负荷逐步自愈恢复 (每秒回 40 点)
            if (guardStrain > 0f)
            {
                guardStrain = Mathf.Max(0f, guardStrain - Time.deltaTime * 40f);
            }

            // 松手后的收招卸劲归正倒计时 (0.24s 内顺畅播放完收招动作后回归待机)
            if (blockRecoveryTimer > 0f)
            {
                blockRecoveryTimer -= Time.deltaTime;
                if (blockRecoveryTimer <= 0f)
                {
                    if (isGrounded && attackTimer <= 0f && !IsBlocking && dodgeTimer <= 0f && stunTimer <= 0f)
                    {
                        currentActionName = "待机 (Idle)";
                    }
                }
            }
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

        // 引剑诀技能 (R 或 P)
        if (Input.GetKeyDown(KeyCode.R) || Input.GetKeyDown(KeyCode.P))
        {
            TriggerYinjianjue();
            return;
        }

        // 以剑御气技能 (G 或 Shift + F)
        if (Input.GetKeyDown(KeyCode.G) || ((Input.GetKey(KeyCode.LeftShift) || Input.GetKey(KeyCode.RightShift)) && Input.GetKeyDown(KeyCode.F)))
        {
            TriggerYijianyuqi();
            return;
        }

        // 万剑归宗终极技能 (Y: 常态/随剑意, V: 强制极·万剑归宗)
        if (Input.GetKeyDown(KeyCode.V))
        {
            TriggerWanjianBloom();
            return;
        }
        if (Input.GetKeyDown(KeyCode.Y))
        {
            TriggerWanjian();
            return;
        }

        // 跳跃 (W / Up / W+Space)
        bool jumpInput = Input.GetKeyDown(KeyCode.W) || Input.GetKeyDown(KeyCode.UpArrow) || (Input.GetKey(KeyCode.W) && Input.GetKeyDown(KeyCode.Space));
        if (jumpInput && isGrounded && dodgeTimer <= 0f)
        {
            blockRecoveryTimer = 0f;
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

        // 格挡架势 (F，未按住 Shift)
        if (Input.GetKeyDown(KeyCode.F) && !Input.GetKey(KeyCode.LeftShift) && !Input.GetKey(KeyCode.RightShift) && isGrounded && dodgeTimer <= 0f && stunTimer <= 0f)
        {
            PerformBlock();
            return;
        }

        // 普通格挡受击响应 (H 或 格挡中按 G 均可模拟受击)
        if ((Input.GetKeyDown(KeyCode.H) || (isBlockingHeld && Input.GetKeyDown(KeyCode.G))) && isGrounded && dodgeTimer <= 0f && stunTimer <= 0f)
        {
            TriggerBlockHit();
            return;
        }

        // 完美弹反成功响应 (T)
        if (Input.GetKeyDown(KeyCode.T) && isGrounded && dodgeTimer <= 0f && stunTimer <= 0f)
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
            blockRecoveryTimer = 0f;
        }
        else
        {
            if (isGrounded && attackTimer <= 0f && !IsBlocking && dodgeTimer <= 0f && stunTimer <= 0f && blockRecoveryTimer <= 0f)
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
        if (stunTimer > 0f) return;
        ExitBlock();
        blockRecoveryTimer = 0f;
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
        if (stunTimer > 0f) return;
        ExitBlock();
        blockRecoveryTimer = 0f;
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
        if (stunTimer > 0f) return;
        ExitBlock();
        blockRecoveryTimer = 0f;
        attackStep = 4;
        attackTimer = 0.76f;
        comboWindow = 0f;
        lungeTimer = 0.18f;
        lungeSpeed = 0.40f / 0.18f;
        currentActionName = "蓄力重刺 (Heavy Thrust)";
        if (animator != null) animator.SetTrigger("HeavyThrust");
    }

    public void PerformBlock(bool fromGui = false)
    {
        if (stunTimer > 0f) return;
        attackStep = 0;
        attackTimer = 0f;
        comboWindow = 0f;
        lungeTimer = 0f;
        blockRecoveryTimer = 0f;
        isBlockingHeld = true;
        isBlockingFromGui = fromGui;
        blockHoldDuration = 0f;
        blockEfficiency = 1.0f;
        blockTimer = 0f;
        currentActionName = "格挡姿态 (Block Guard)";
        if (animator != null)
        {
            animator.SetBool("IsBlocking", true);
            animator.SetTrigger("Block");
        }
    }

    public void ExitBlock()
    {
        if (isBlockingHeld || blockTimer > 0f)
        {
            blockRecoveryTimer = 0.24f; // 卸劲归正收招动画时长 (0.24s 播放 guard-5 -> guard-6 -> guard-7 -> Idle)
            currentActionName = "收招卸劲 (Block Exit)";
        }
        isBlockingHeld = false;
        isBlockingFromGui = false;
        blockTimer = 0f;
        blockHoldDuration = 0f;
        blockEfficiency = 1.0f;
        if (animator != null)
        {
            animator.SetBool("IsBlocking", false);
        }
    }

    public void TriggerBlockHit()
    {
        if (stunTimer > 0f) return;
        attackStep = 0;
        attackTimer = 0f;
        comboWindow = 0f;
        lungeTimer = 0f;

        // 如果在弹反窗内受击，直接化为弹反成功
        if (IsBlocking && blockHoldDuration <= ParryWindow)
        {
            TriggerParrySuccess();
            return;
        }

        // 受到攻击增加架势负荷：基础 32 点；持盾越久效能越弱，承受负荷成反比急剧增大（最高放大 3.3 倍）
        float strainAdded = 32f * (1.0f / Mathf.Max(0.25f, blockEfficiency));
        guardStrain += strainAdded;

        // 受到一定攻击架势负荷爆满（>=100）：【强制结束弹刀，并且僵直】！
        if (guardStrain >= 100f)
        {
            TriggerGuardBreak();
            return;
        }

        blockTimer = 0.30f;
        currentActionName = $"普通格挡受击 (效能:{Mathf.RoundToInt(blockEfficiency * 100)}% 负荷:{Mathf.RoundToInt(guardStrain)}/100)";
        if (animator != null)
        {
            animator.SetTrigger("BlockHit");
        }
    }

    public void TriggerGuardBreak()
    {
        isBlockingHeld = false;
        isBlockingFromGui = false;
        blockTimer = 0f;
        blockHoldDuration = 0f;
        blockRecoveryTimer = 0f;
        guardStrain = 100f;
        stunTimer = GuardBreakStunDuration; // 1.25秒破防僵直
        currentActionName = "【弹刀破防！】架势崩解僵直！";

        if (animator != null)
        {
            animator.SetBool("IsBlocking", false);
            animator.ResetTrigger("Block");
            animator.Play("BlockHit", 0, 0f);
        }

        // 弹刀受力后退震退
        float pushDir = (spriteRenderer != null && spriteRenderer.flipX) ? 1f : -1f;
        Vector3 p = transform.position;
        p.x += pushDir * 0.40f;
        transform.position = p;
    }

    public void TriggerParrySuccess()
    {
        if (stunTimer > 0f) return;
        attackStep = 0;
        attackTimer = 0f;
        comboWindow = 0f;
        lungeTimer = 0f;
        guardStrain = Mathf.Max(0f, guardStrain - 30f); // 弹反成功大幅化解架势负荷
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
        if (pokongciSprites == null || pokongciSprites.Length < 8 || pokongciSprites[0] == null)
        {
            LoadPokongciSprites();
        }

        isSkillPlaying = true;
        currentActionName = "【剑技】破空刺 · 错身瞬透 (Piercing Void Thrust)";

        Vector3 startP = transform.position;
        float faceDir = spriteRenderer != null && spriteRenderer.flipX ? -1f : 1f;
        Vector3 targetEndP = startP + new Vector3(faceDir * 1.3f, 0f, 0f);
        Sprite activeSp = spriteRenderer != null ? spriteRenderer.sprite : null;

        // 启动常态破空刺专属特效（细青白激光线 + 2重残影 + 敌后延时裂体墨爆）
        PokongciBloomFX.Instance.PlayNormalPokongciFX(transform, spriteRenderer != null && spriteRenderer.flipX, startP, targetEndP, activeSp);

        if (pokongciSprites != null && pokongciSprites.Length >= 8)
        {
            if (animator != null) animator.enabled = false;

            // 极速起手(5f) -> 离弦飞身(5f, +0.35m) -> 电光贯体(5f, +0.65m) -> 敌后单膝刹车(6f, +0.30m) -> 延时墨爆(8f) -> 旋剑抽意(7f) -> 拂袖导刃(7f) -> 敛息归渊(9f)
            float[] frameDurations = new float[] { 0.05f, 0.05f, 0.05f, 0.06f, 0.08f, 0.07f, 0.07f, 0.09f };
            float[] frameLunges = new float[] { 0f, 0.35f, 0.65f, 0.30f, 0.0f, 0.0f, 0.0f, 0.0f }; // 总位移 1.3m，直接穿透至敌后

            for (int i = 0; i < 8; i++)
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
        if (pokongciBloomSprites == null || pokongciBloomSprites.Length < 8 || pokongciBloomSprites[0] == null)
        {
            LoadPokongciBloomSprites();
        }

        isSkillPlaying = true;
        currentActionName = "【剑意绽放】极·破空刺 (Void Thrust · Bloom)";
        swordIntent = 0; // 消耗 5 阶剑意

        Vector3 startP = transform.position;
        float faceDir = spriteRenderer != null && spriteRenderer.flipX ? -1f : 1f;
        Vector3 targetEndP = startP + new Vector3(faceDir * 1.8f, 0f, 0f);
        Sprite activeSp = spriteRenderer != null ? spriteRenderer.sprite : null;

        // 启动电影级全套特效（四灵飞剑+天崩巨锥+时空停滞+三度墨爆+空间裂隙+冰霜霜痕+残影）
        PokongciBloomFX.Instance.PlayBloomEffect(transform, spriteRenderer != null && spriteRenderer.flipX, startP, targetEndP, activeSp);

        if (pokongciBloomSprites != null && pokongciBloomSprites.Length >= 8)
        {
            if (animator != null) animator.enabled = false;

            // 刚体聚势闪烁 (青金刚体光辉)
            if (spriteRenderer != null) spriteRenderer.color = new Color(0.6f, 1f, 1f, 1f);

            // 强化版位移翻倍至 1.8m，穿透一切敌人 (8帧序列)
            // F1: 极·起势·龙吟聚风 (0.06s, lunge 0.0m)
            // F2: 极·离弦·金芒破空 (0.05s, lunge 0.50m)
            // F3: 极·贯体·错身碎空 (0.05s, lunge 0.85m)
            // F4: 极·止步·金刚逆滑 (0.07s, lunge 0.45m -> 总位移 1.80m) + 时空凝滞/慢放
            // F5: 极·裂体·暗渊沉爆 (0.08s)
            // F6: 极·回锋·金墨断脉 (0.08s) -> 三度连环墨爆闪烁
            // F7: 极·霜界·玄冰冻空 (0.08s)
            // F8: 极·纳鞘·万象定乾坤 (0.10s)
            float[] frameDurations = new float[] { 0.06f, 0.05f, 0.05f, 0.07f, 0.08f, 0.08f, 0.08f, 0.10f };
            float[] frameLunges = new float[] { 0f, 0.50f, 0.85f, 0.45f, 0.0f, 0.0f, 0.0f, 0.0f }; // 总位移 1.8m

            // P1~P3 聚势与离弦
            for (int i = 0; i < 3; i++)
            {
                if (spriteRenderer != null) spriteRenderer.sprite = pokongciBloomSprites[i];
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

            // P4 瞬身穿透 + 止步跪滑 + 6f 时空静止 (Chrono Pause)
            if (spriteRenderer != null)
            {
                spriteRenderer.sprite = pokongciBloomSprites[3];
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

            // P5 裂痕蓄爆与共振 (暗渊沉爆)
            if (spriteRenderer != null) spriteRenderer.sprite = pokongciBloomSprites[4];
            yield return new WaitForSeconds(frameDurations[4]);

            // P6 三度连环墨爆 (三次闪烁与音画震颤)
            currentActionName = "【剑痕引爆】三度断空墨爆！";
            if (spriteRenderer != null) spriteRenderer.sprite = pokongciBloomSprites[5];
            for (int blast = 1; blast <= 3; blast++)
            {
                if (spriteRenderer != null) spriteRenderer.color = new Color(0.3f, 0.9f, 1f);
                yield return new WaitForSeconds(0.04f);
                if (spriteRenderer != null) spriteRenderer.color = Color.white;
                yield return new WaitForSeconds(0.03f);
            }

            // P7 霜界玄冰冻空
            if (spriteRenderer != null) spriteRenderer.sprite = pokongciBloomSprites[6];
            yield return new WaitForSeconds(frameDurations[6]);

            // P8 纳鞘定乾坤与散尘入鞘
            if (spriteRenderer != null) spriteRenderer.sprite = pokongciBloomSprites[7];
            yield return new WaitForSeconds(frameDurations[7]);

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
        if (huifengwuBloomSprites == null || huifengwuBloomSprites.Length < 8 || huifengwuBloomSprites[0] == null)
        {
            LoadHuifengwuBloomSprites();
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

        if (isBloom)
        {
            if (huifengwuBloomSprites == null || huifengwuBloomSprites.Length < 8 || huifengwuBloomSprites[0] == null)
            {
                LoadHuifengwuBloomSprites();
            }
        }
        else
        {
            if (huifengwuSprites == null || huifengwuSprites.Length < 8 || huifengwuSprites[0] == null)
            {
                LoadHuifengwuSprites();
            }
        }

        if (animator != null) animator.enabled = false;

        // 触发回风舞专属特效（月牙斩芒、交错斩光与剑尖星爆）
        PokongciBloomFX.Instance.PlayHuifengwuFX(transform, isBloom);

        Vector3 basePos = transform.position;
        bool origFlip = spriteRenderer != null && spriteRenderer.flipX;

        Sprite[] activeSprites = (isBloom && huifengwuBloomSprites != null && huifengwuBloomSprites.Length >= 8 && huifengwuBloomSprites[0] != null)
            ? huifengwuBloomSprites
            : huifengwuSprites;

        if (activeSprites != null && activeSprites.Length >= 8 && activeSprites[0] != null)
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
                    spriteRenderer.sprite = activeSprites[i];
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
        if (isBloomActive)
        {
            TriggerYijianshuanghanBloom();
            return;
        }

        if (yijianshuanghanSprites == null || yijianshuanghanSprites.Length < 8 || yijianshuanghanSprites[0] == null)
        {
            LoadYijianshuanghanSprites();
        }
        attackStep = 0;
        attackTimer = 0f;
        comboWindow = 0f;
        blockTimer = 0f;
        dodgeTimer = 0f;
        StartCoroutine(YijianshuanghanRoutine(false));
    }

    public void TriggerYijianshuanghanBloom()
    {
        if (isSkillPlaying) return;
        if (yijianshuanghanBloomSprites == null || yijianshuanghanBloomSprites.Length < 8 || yijianshuanghanBloomSprites[0] == null)
        {
            LoadYijianshuanghanBloomSprites();
        }
        swordIntent = 5;
        attackStep = 0;
        attackTimer = 0f;
        comboWindow = 0f;
        blockTimer = 0f;
        dodgeTimer = 0f;
        StartCoroutine(YijianshuanghanRoutine(true));
    }

    IEnumerator YijianshuanghanRoutine(bool isBloom)
    {
        isSkillPlaying = true;
        currentActionName = isBloom ? "极·一剑霜寒（绝对霜冻·冰魄玄峰）" : "一剑霜寒 (Frostbound Slash · 蓄力霜线)";
        if (isBloom) swordIntent = 0;

        Sprite[] activeSprites = isBloom ? yijianshuanghanBloomSprites : yijianshuanghanSprites;
        if (activeSprites == null || activeSprites.Length < 8 || activeSprites[0] == null)
        {
            if (isBloom) LoadYijianshuanghanBloomSprites();
            else LoadYijianshuanghanSprites();
            activeSprites = isBloom ? yijianshuanghanBloomSprites : yijianshuanghanSprites;
        }

        if (animator != null) animator.enabled = false;

        Vector3 basePos = transform.position;
        bool origFlip = spriteRenderer != null && spriteRenderer.flipX;
        float faceDir = origFlip ? -1f : 1f;

        if (activeSprites != null && activeSprites.Length >= 8 && activeSprites[0] != null)
        {
            float[] frameDurations = isBloom 
                ? new float[] { 0.12f, 0.14f, 0.18f, 0.10f, 0.12f, 0.16f, 0.14f, 0.18f }
                : new float[] { 0.10f, 0.13f, 0.18f, 0.09f, 0.11f, 0.13f, 0.13f, 0.16f };

            for (int i = 0; i < 8; i++)
            {
                if (spriteRenderer != null)
                {
                    spriteRenderer.sprite = activeSprites[i];
                    if (isBloom && (i == 2 || i == 3 || i == 4))
                    {
                        spriteRenderer.color = new Color(0.75f, 0.95f, 1f, 1f);
                    }
                    else
                    {
                        spriteRenderer.color = Color.white;
                    }
                }

                // F4 斩出瞬间 Hitstop (顿帧)
                if (i == 3)
                {
                    Time.timeScale = isBloom ? 0.20f : 0.25f;
                    yield return new WaitForSecondsRealtime(isBloom ? 0.06f : 0.04f);
                    Time.timeScale = 1.0f;
                }

                // F5 前刺冲刷位移
                if (i == 4)
                {
                    Vector3 p = transform.position;
                    p.x += faceDir * (isBloom ? 0.55f : 0.35f);
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

    public void TriggerYinjianjue()
    {
        if (isSkillPlaying) return;
        if (isBloomActive)
        {
            TriggerYinjianjueBloom();
            return;
        }

        if (yinjianjueSprites == null || yinjianjueSprites.Length < 8 || yinjianjueSprites[0] == null)
        {
            LoadYinjianjueSprites();
        }
        attackStep = 0;
        attackTimer = 0f;
        comboWindow = 0f;
        blockTimer = 0f;
        dodgeTimer = 0f;
        StartCoroutine(YinjianjueRoutine());
    }

    public void TriggerYinjianjueBloom()
    {
        if (isSkillPlaying) return;
        if (yinjianjueBloomSprites == null || yinjianjueBloomSprites.Length < 8 || yinjianjueBloomSprites[0] == null)
        {
            LoadYinjianjueBloomSprites();
        }
        swordIntent = 5;
        attackStep = 0;
        attackTimer = 0f;
        comboWindow = 0f;
        blockTimer = 0f;
        dodgeTimer = 0f;
        StartCoroutine(YinjianjueBloomRoutine());
    }


    IEnumerator YinjianjueRoutine()
    {
        isSkillPlaying = true;
        currentActionName = "【剑技】引剑诀 · 流光溯影 (Radiant Flying Sword Recall)";

        if (yinjianjueSprites == null || yinjianjueSprites.Length < 8 || yinjianjueSprites[0] == null)
        {
            LoadYinjianjueSprites();
        }

        if (animator != null) animator.enabled = false;

        Vector3 basePos = transform.position;
        bool origFlip = spriteRenderer != null && spriteRenderer.flipX;

        if (yinjianjueSprites != null && yinjianjueSprites.Length >= 8 && yinjianjueSprites[0] != null)
        {
            // 8 阶段时序：
            // F1: 结印·引灵指 (0.12s) - 手中无剑，剑指横胸聚气
            // F2: 遥召·破空鸣 (0.12s) - 剑指前伸，空气音爆波纹
            // F3: 牵引·流光穿 (0.14s) - 飞剑横贯全屏穿透强袭
            // F4: 候刃·展臂迎 (0.10s) - 飞剑临近，展臂虚抓
            // F5: 握柄·雷爆定 (0.18s) - 五指暴握剑柄！金属入鞘声 + 环形冲击波 + 0.08s时空停滞
            // F6: 旋腕·剑花破 (0.12s) - 顺势反手挽出360°水墨残月剑花
            // F7: 拂袖·振刃鸣 (0.12s) - 大袖拂过剑脊，剑鸣阵阵
            // F8: 敛息·垂剑立 (0.16s) - 从容反手垂剑，气沉丹田切回待机
            float[] frameDurations = new float[] { 0.12f, 0.12f, 0.14f, 0.10f, 0.18f, 0.12f, 0.12f, 0.16f };

            // F1: 结印·引灵指 (0.12s) - 手中无剑，剑指横胸聚气，指尖灵光凝聚
            if (spriteRenderer != null) spriteRenderer.sprite = yinjianjueSprites[0];
            PokongciBloomFX.Instance.PlayYinjianjueF1Gather(transform, origFlip);
            yield return new WaitForSeconds(frameDurations[0]);

            // F2: 遥召·破空鸣 (0.12s) - 剑指前伸凌空遥指，音爆波纹扩散呼啸唤剑
            if (spriteRenderer != null) spriteRenderer.sprite = yinjianjueSprites[1];
            PokongciBloomFX.Instance.PlayYinjianjueF2SonicBoom(transform, origFlip);
            yield return new WaitForSeconds(frameDurations[1]);

            // F3: 牵引·流光穿 (0.14s) - 飞剑横贯全屏高速呼啸而来！白虹贯日！
            if (spriteRenderer != null) spriteRenderer.sprite = yinjianjueSprites[2];
            float flightDuration = frameDurations[2] + frameDurations[3]; // F3+F4 共 0.24s 穿透全屏精准归手
            PokongciBloomFX.Instance.LaunchYinjianjueFlyingSword(transform, origFlip, flightDuration);
            yield return new WaitForSeconds(frameDurations[2]);

            // F4: 候刃·展臂迎 (0.10s) - 飞剑临近掌心，真气剧烈压缩爆发出耀眼摩擦火花
            if (spriteRenderer != null) spriteRenderer.sprite = yinjianjueSprites[3];
            yield return new WaitForSeconds(frameDurations[3]);

            // F5: 握柄·雷爆定 (0.18s) - 五指死死咬合剑柄！环形水墨冲击波 + 0.08s全屏时空停滞
            currentActionName = "【飞剑归渊】万钧合刃！";
            if (spriteRenderer != null)
            {
                spriteRenderer.sprite = yinjianjueSprites[4];
                spriteRenderer.color = new Color(0.4f, 1f, 1f, 1f); // 耀目光华
            }
            PokongciBloomFX.Instance.PlayYinjianjueF5Catch(transform, origFlip);
            Time.timeScale = 0.2f;
            yield return new WaitForSecondsRealtime(0.08f);
            Time.timeScale = 1.0f;
            if (spriteRenderer != null) spriteRenderer.color = Color.white;
            yield return new WaitForSeconds(frameDurations[4]);

            // F6: 旋腕·剑花破 (0.12s) - 借回握惯性顺势反手挽出 360° 水墨残月剑花
            if (spriteRenderer != null) spriteRenderer.sprite = yinjianjueSprites[5];
            PokongciBloomFX.Instance.PlayYinjianjueF6SwordFlourish(transform, origFlip);
            yield return new WaitForSeconds(frameDurations[5]);

            // F7: 拂袖·振刃鸣 (0.12s) - 大袖拂过剑脊，剑鸣阵阵，碎钻星尘粒子飘落
            if (spriteRenderer != null) spriteRenderer.sprite = yinjianjueSprites[6];
            PokongciBloomFX.Instance.PlayYinjianjueF7Stardust(transform, origFlip);
            yield return new WaitForSeconds(frameDurations[6]);

            // F8: 敛息·垂剑立 (0.16s) - 从容反手垂剑，气沉丹田，无缝归入待机
            if (spriteRenderer != null) spriteRenderer.sprite = yinjianjueSprites[7];
            yield return new WaitForSeconds(frameDurations[7]);
        }
        else
        {
            if (animator != null)
            {
                animator.enabled = true;
                animator.Play("HeavyThrust", 0, 0f);
            }
            yield return new WaitForSeconds(0.40f);
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

    IEnumerator YinjianjueBloomRoutine()
    {
        isSkillPlaying = true;
        currentActionName = "【剑意绽放】极·万剑归宗 (混元归渊 · 冰破乾坤)";
        swordIntent = 0; // 消耗 5 阶剑意

        if (yinjianjueBloomSprites == null || yinjianjueBloomSprites.Length < 8 || yinjianjueBloomSprites[0] == null)
        {
            LoadYinjianjueBloomSprites();
        }

        if (animator != null) animator.enabled = false;

        Vector3 basePos = transform.position;
        bool origFlip = spriteRenderer != null && spriteRenderer.flipX;

        if (yinjianjueBloomSprites != null && yinjianjueBloomSprites.Length >= 8 && yinjianjueBloomSprites[0] != null)
        {
            // 8 阶段时序：
            // F1: 剑阵起势·万道朝宗 (0.10s)
            // F2: 雷霆破晓·神剑初醒 (0.12s)
            // F3: 白虹贯日·太虚横空 (0.14s)
            // F4: 混元归渊·诸天合一 (0.12s)
            // F5: 极·万钧合刃·冰破乾坤 (0.20s)
            // F6: 八荒扫尽·万劫成空 (0.14s)
            // F7: 龙吟归袖·风雷渐歇 (0.14s)
            // F8: 万道归一·天人合道 (0.18s)
            float[] frameDurations = new float[] { 0.10f, 0.12f, 0.14f, 0.12f, 0.20f, 0.14f, 0.14f, 0.18f };

            // 绽放专属青金神光
            if (spriteRenderer != null) spriteRenderer.color = new Color(0.7f, 1f, 1f, 1f);

            // F1: 剑阵起势 (0.10s)
            if (spriteRenderer != null) spriteRenderer.sprite = yinjianjueBloomSprites[0];
            PokongciBloomFX.Instance.PlayYinjianjueF1Gather(transform, origFlip);
            yield return new WaitForSeconds(frameDurations[0]);

            // F2: 雷霆破晓 (0.12s)
            if (spriteRenderer != null) spriteRenderer.sprite = yinjianjueBloomSprites[1];
            PokongciBloomFX.Instance.PlayYinjianjueF2SonicBoom(transform, origFlip);
            PokongciBloomFX.Instance.TriggerCameraShake(0.18f, 0.08f);
            yield return new WaitForSeconds(frameDurations[1]);

            // F3: 白虹贯日 (0.14s) - 混元万剑齐发贯穿全屏
            if (spriteRenderer != null) spriteRenderer.sprite = yinjianjueBloomSprites[2];
            float flightDuration = frameDurations[2] + frameDurations[3]; // 0.26s
            PokongciBloomFX.Instance.LaunchYinjianjueBloomSwordTempest(transform, origFlip, flightDuration);
            yield return new WaitForSeconds(frameDurations[2]);

            // F4: 混元归渊 (0.12s)
            if (spriteRenderer != null) spriteRenderer.sprite = yinjianjueBloomSprites[3];
            yield return new WaitForSeconds(frameDurations[3]);

            // F5: 极·万钧合刃 (0.20s) - 双层金青震波 + 巨型极光星芒 + 顿帧0.12s
            currentActionName = "【万剑归宗】极·万钧合刃！";
            if (spriteRenderer != null)
            {
                spriteRenderer.sprite = yinjianjueBloomSprites[4];
                spriteRenderer.color = new Color(0.4f, 1f, 1f, 1f);
            }
            PokongciBloomFX.Instance.PlayYinjianjueBloomF5Catch(transform, origFlip);
            Time.timeScale = 0.15f;
            yield return new WaitForSecondsRealtime(0.12f);
            Time.timeScale = 1.0f;
            if (spriteRenderer != null) spriteRenderer.color = new Color(0.8f, 1f, 1f, 1f);
            yield return new WaitForSeconds(frameDurations[4]);

            // F6: 八荒扫尽 (0.14s) - 双重金青太虚残月剑气
            if (spriteRenderer != null) spriteRenderer.sprite = yinjianjueBloomSprites[5];
            PokongciBloomFX.Instance.PlayYinjianjueBloomF6Flourish(transform, origFlip);
            yield return new WaitForSeconds(frameDurations[5]);

            // F7: 龙吟归袖 (0.14s)
            if (spriteRenderer != null) spriteRenderer.sprite = yinjianjueBloomSprites[6];
            PokongciBloomFX.Instance.PlayYinjianjueF7Stardust(transform, origFlip);
            yield return new WaitForSeconds(frameDurations[6]);

            // F8: 万道归一 (0.18s)
            if (spriteRenderer != null) spriteRenderer.sprite = yinjianjueBloomSprites[7];
            yield return new WaitForSeconds(frameDurations[7]);
        }
        else
        {
            if (animator != null)
            {
                animator.enabled = true;
                animator.Play("HeavyThrust", 0, 0f);
            }
            yield return new WaitForSeconds(0.40f);
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

    public void TriggerYijianyuqi(bool fromGui = false)
    {
        if (isSkillPlaying) return;
        if (isBloomActive)
        {
            TriggerYijianyuqiBloom(fromGui);
            return;
        }

        if (yijianyuqiSprites == null || yijianyuqiSprites.Length < 16 || yijianyuqiSprites[0] == null)
        {
            LoadYijianyuqiSprites();
        }
        isYuqiFromGui = fromGui;
        attackStep = 0;
        attackTimer = 0f;
        comboWindow = 0f;
        blockTimer = 0f;
        dodgeTimer = 0f;
        StartCoroutine(YijianyuqiRoutine());
    }

    public void TriggerYijianyuqiBloom(bool fromGui = false)
    {
        if (isSkillPlaying) return;
        if (yijianyuqiBloomSprites == null || yijianyuqiBloomSprites.Length < 16 || yijianyuqiBloomSprites[0] == null)
        {
            LoadYijianyuqiBloomSprites();
        }
        isYuqiFromGui = fromGui;
        swordIntent = 5;
        attackStep = 0;
        attackTimer = 0f;
        comboWindow = 0f;
        blockTimer = 0f;
        dodgeTimer = 0f;
        StartCoroutine(YijianyuqiBloomRoutine());
    }

    public void AbsorbYuqiHit(float dmg, bool isBloom)
    {
        if (isBloom)
        {
            yuqiBloomAbsorbedDamage += dmg;
            StartCoroutine(FlashYuqiColor(new Color(0.4f, 0.95f, 1f)));
        }
        else
        {
            yuqiAbsorbedDamage += dmg;
            StartCoroutine(FlashYuqiColor(new Color(0.3f, 1f, 0.85f)));
        }
    }

    IEnumerator FlashYuqiColor(Color flashCol)
    {
        if (spriteRenderer != null)
        {
            Color prev = spriteRenderer.color;
            spriteRenderer.color = flashCol;
            yield return new WaitForSecondsRealtime(0.06f);
            if (spriteRenderer != null) spriteRenderer.color = prev;
        }
    }

    IEnumerator YijianyuqiRoutine()
    {
        isSkillPlaying = true;
        isYuqiShieldActive = false;
        yuqiAbsorbedDamage = 0f;
        currentActionName = "【剑技】以剑御气 · 苍龙玄天钟 (起势构盾)";

        if (yijianyuqiSprites == null || yijianyuqiSprites.Length < 16 || yijianyuqiSprites[0] == null)
        {
            LoadYijianyuqiSprites();
        }

        if (animator != null) animator.enabled = false;
        bool origFlip = spriteRenderer != null && spriteRenderer.flipX;

        if (yijianyuqiSprites != null && yijianyuqiSprites.Length >= 16 && yijianyuqiSprites[0] != null)
        {
            // 阶段一：构盾前摇 (F1 ~ F4，以剑引气，双龙合钟)
            float[] startupDurations = new float[] { 0.06f, 0.06f, 0.06f, 0.06f };
            for (int i = 0; i < 4; i++)
            {
                if (spriteRenderer != null) spriteRenderer.sprite = yijianyuqiSprites[i];
                yield return new WaitForSeconds(startupDurations[i]);
            }

            // 阶段二：琉璃玄钟护盾固守 (F5 ~ F7 维持阶段)
            // 设定：按住不松时一直维持护盾，不随时间衰减，吸收所有伤害，超限或松手完成剩下动作
            isYuqiShieldActive = true;
            int[] holdFrames = new int[] { 4, 5, 6 }; // F5, F6, F7
            int holdIdx = 0;
            float frameTimer = 0f;
            const float holdFrameDuration = 0.14f; // 护盾晶格与苍龙游弋呼吸循环
            bool shieldOverloaded = false;

            while (true)
            {
                // 检测按键是否持续按住 (G 键 或 Shift + F，或 GUI 保持)
                bool isKeyHeld = Input.GetKey(KeyCode.G) ||
                                 ((Input.GetKey(KeyCode.LeftShift) || Input.GetKey(KeyCode.RightShift)) && Input.GetKey(KeyCode.F)) ||
                                 isYuqiFromGui;

                // 松开按键：退出护盾维持，完成剩下动作
                if (!isKeyHeld)
                {
                    shieldOverloaded = false;
                    break;
                }

                // 受到伤害超出范围 (达到或超过上限 maxYuqiShield 100点)：聚能临界爆裂，完成剩下动作
                if (yuqiAbsorbedDamage >= maxYuqiShield)
                {
                    shieldOverloaded = true;
                    break;
                }

                // 允许按 H 键模拟受击吸收伤害 (每次吸收 25 点)
                if (Input.GetKeyDown(KeyCode.H))
                {
                    AbsorbYuqiHit(25f, false);
                }

                // 呼吸循环动画渲染
                frameTimer += Time.deltaTime;
                if (frameTimer >= holdFrameDuration)
                {
                    frameTimer = 0f;
                    holdIdx = (holdIdx + 1) % holdFrames.Length;
                    if (spriteRenderer != null) spriteRenderer.sprite = yijianyuqiSprites[holdFrames[holdIdx]];
                }

                currentActionName = $"【以剑御气·苍龙玄天钟】护盾固守 (吸收: {Mathf.RoundToInt(yuqiAbsorbedDamage)}/{Mathf.RoundToInt(maxYuqiShield)} | 效能: 100% 无衰减 | H 模拟受击)";

                yield return null;
            }

            isYuqiShieldActive = false;
            isYuqiFromGui = false;

            // 阶段三：承击逆震与完成剩下动作 (F8 ~ F16)
            if (shieldOverloaded)
            {
                currentActionName = "【玄钟聚能临界爆裂！】苍龙破壁大反震！";
            }
            else
            {
                currentActionName = "【松手收势逆震】暴烈推刃！苍龙破壁！";
            }

            // F8 (index 7: 触界星爆 / 临界迸发)
            if (spriteRenderer != null) spriteRenderer.sprite = yijianyuqiSprites[7];
            yield return new WaitForSeconds(0.08f);

            // F9 (index 8: 墨痕裂钟 - 强烈停顿顿帧)
            if (spriteRenderer != null) spriteRenderer.sprite = yijianyuqiSprites[8];
            Time.timeScale = 0.2f;
            yield return new WaitForSecondsRealtime(0.08f);
            Time.timeScale = 1.0f;

            // F10 ~ F16 (index 9 ~ 15) 完成剩下反震推刃、漫天碎晶与收剑归鞘动作
            float[] finishDurations = new float[] {
                0.07f, // F10 暴烈推刃
                0.08f, // F11 龙吟破壁
                0.09f, // F12 漫天碎晶
                0.07f, // F13 星尘飞瀑
                0.09f, // F14 狂草残月 360度剑花
                0.08f, // F15 龙吟振雪
                0.12f  // F16 敛息入道
            };

            for (int i = 9; i < 16; i++)
            {
                if (spriteRenderer != null) spriteRenderer.sprite = yijianyuqiSprites[i];
                yield return new WaitForSeconds(finishDurations[i - 9]);
            }
        }
        else
        {
            if (animator != null) { animator.enabled = true; animator.Play("Block", 0, 0f); }
            yield return new WaitForSeconds(0.40f);
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

    IEnumerator YijianyuqiBloomRoutine()
    {
        isSkillPlaying = true;
        isYuqiBloomShieldActive = false;
        yuqiBloomAbsorbedDamage = 0f;
        currentActionName = "【剑意绽放】极·以剑御气 · 万仞诛魔金刚剑界 (起势构界)";
        swordIntent = 0;

        if (yijianyuqiBloomSprites == null || yijianyuqiBloomSprites.Length < 16 || yijianyuqiBloomSprites[0] == null)
        {
            LoadYijianyuqiBloomSprites();
        }

        if (animator != null) animator.enabled = false;
        bool origFlip = spriteRenderer != null && spriteRenderer.flipX;

        if (yijianyuqiBloomSprites != null && yijianyuqiBloomSprites.Length >= 16 && yijianyuqiBloomSprites[0] != null)
        {
            // 阶段一：金刚剑界起势 (F1 ~ F4，星斗太极，神霄天雷，八剑起势)
            float[] startupDurations = new float[] { 0.06f, 0.06f, 0.06f, 0.06f };
            for (int i = 0; i < 4; i++)
            {
                if (spriteRenderer != null) spriteRenderer.sprite = yijianyuqiBloomSprites[i];
                yield return new WaitForSeconds(startupDurations[i]);
            }

            // 阶段二：万仞剑界金刚护体 (F5 ~ F7 维持阶段)
            // 8柄神圣青金飞剑公转，万仞刺林光轮；按住维持，无时间衰减，吸收所有伤害
            isYuqiBloomShieldActive = true;
            int[] holdFrames = new int[] { 4, 5, 6 }; // F5, F6, F7
            int holdIdx = 0;
            float frameTimer = 0f;
            const float holdFrameDuration = 0.12f;
            bool shieldOverloaded = false;

            while (true)
            {
                bool isKeyHeld = Input.GetKey(KeyCode.G) ||
                                 ((Input.GetKey(KeyCode.LeftShift) || Input.GetKey(KeyCode.RightShift)) && Input.GetKey(KeyCode.F)) ||
                                 isYuqiFromGui;

                if (!isKeyHeld)
                {
                    shieldOverloaded = false;
                    break;
                }

                if (yuqiBloomAbsorbedDamage >= maxYuqiBloomShield)
                {
                    shieldOverloaded = true;
                    break;
                }

                if (Input.GetKeyDown(KeyCode.H))
                {
                    AbsorbYuqiHit(30f, true);
                }

                frameTimer += Time.deltaTime;
                if (frameTimer >= holdFrameDuration)
                {
                    frameTimer = 0f;
                    holdIdx = (holdIdx + 1) % holdFrames.Length;
                    if (spriteRenderer != null) spriteRenderer.sprite = yijianyuqiBloomSprites[holdFrames[holdIdx]];
                }

                currentActionName = $"【极·以剑御气·万仞诛魔剑界】金刚剑界护体 (吸收: {Mathf.RoundToInt(yuqiBloomAbsorbedDamage)}/{Mathf.RoundToInt(maxYuqiBloomShield)} | 效能: 100% 无衰减 | H 模拟受击)";

                yield return null;
            }

            isYuqiBloomShieldActive = false;
            isYuqiFromGui = false;

            // 阶段三：万仞碎空与完成剩下动作 (F8 ~ F16)
            if (shieldOverloaded)
            {
                currentActionName = "【剑界聚能临界爆裂！】万仞碎空超新星！";
            }
            else
            {
                currentActionName = "【万仞诛魔 · 极空推刃！】超新星大核爆！";
            }

            // F8 (index 7: 虚空裂隙触界星爆)
            if (spriteRenderer != null) spriteRenderer.sprite = yijianyuqiBloomSprites[7];
            yield return new WaitForSeconds(0.08f);

            // F9 (index 8: 时空凝滞临界极核 - 极致时停)
            if (spriteRenderer != null) spriteRenderer.sprite = yijianyuqiBloomSprites[8];
            Time.timeScale = 0.1f;
            yield return new WaitForSecondsRealtime(0.12f);
            Time.timeScale = 1.0f;

            // F10 ~ F16 (index 9 ~ 15) 完成剩下动作
            float[] finishDurations = new float[] {
                0.07f, // F10 万仞碎空超新星大核爆
                0.08f, // F11 拔地 2 米冰魄玄峰神峰群
                0.10f, // F12 银河碎晶倒泻
                0.07f, // F13 双层太虚残月剑幕
                0.09f, // F14 神剑龙吟
                0.08f, // F15 天人合道
                0.12f  // F16 敛息归鞘
            };

            for (int i = 9; i < 16; i++)
            {
                if (spriteRenderer != null) spriteRenderer.sprite = yijianyuqiBloomSprites[i];
                yield return new WaitForSeconds(finishDurations[i - 9]);
            }
        }
        else
        {
            if (animator != null) { animator.enabled = true; animator.Play("HeavyThrust", 0, 0f); }
            yield return new WaitForSeconds(0.40f);
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

    public void TriggerWanjian()
    {
        if (isSkillPlaying) return;
        if (swordIntent >= 5)
        {
            TriggerWanjianBloom();
            return;
        }
        if (wanjianSprites == null || wanjianSprites.Length < 16 || wanjianSprites[0] == null)
        {
            LoadWanjianSprites();
        }
        attackStep = 0;
        attackTimer = 0f;
        comboWindow = 0f;
        dodgeTimer = 0f;
        StartCoroutine(WanjianRoutine());
    }

    public void TriggerWanjianBloom()
    {
        if (isSkillPlaying) return;
        if (wanjianBloomSprites == null || wanjianBloomSprites.Length < 16 || wanjianBloomSprites[0] == null)
        {
            LoadWanjianBloomSprites();
        }
        attackStep = 0;
        attackTimer = 0f;
        comboWindow = 0f;
        dodgeTimer = 0f;
        swordIntent = 5;
        StartCoroutine(WanjianBloomRoutine());
    }

    IEnumerator WanjianRoutine()
    {
        isSkillPlaying = true;
        currentActionName = "【终极奥义】万剑归宗 · 剑雨倾天 (QF-6)";

        if (wanjianSprites == null || wanjianSprites.Length < 16 || wanjianSprites[0] == null)
        {
            LoadWanjianSprites();
        }
        if (fallingSwordNormal45Sprite == null) LoadWanjianProjectiles();

        if (animator != null) animator.enabled = false;
        bool origFlip = spriteRenderer != null && spriteRenderer.flipX;
        float faceDir = origFlip ? -1f : 1f;

        if (wanjianSprites != null && wanjianSprites.Length >= 16 && wanjianSprites[0] != null)
        {
            // 阶段一：起势·踏空引天 (F1 ~ F4)
            float[] startupDurations = new float[] { 0.08f, 0.08f, 0.08f, 0.08f };
            for (int i = 0; i < 4; i++)
            {
                if (spriteRenderer != null) spriteRenderer.sprite = wanjianSprites[i];
                yield return new WaitForSeconds(startupDurations[i]);
            }

            // 阶段二：覆掌与暴雨贯地 (F5 ~ F8)
            float[] barrageDurations = new float[] { 0.08f, 0.08f, 0.08f, 0.08f };
            for (int i = 4; i < 8; i++)
            {
                if (spriteRenderer != null) spriteRenderer.sprite = wanjianSprites[i];
                StartCoroutine(SpawnFallingSwordRain(false, 4, faceDir));
                PokongciBloomFX.Instance.TriggerCameraShake(0.14f, 0.06f);
                yield return new WaitForSeconds(barrageDurations[i - 4]);
            }

            // 阶段三：剑阵插地与太虚大爆破 (F9 ~ F12)
            if (spriteRenderer != null) spriteRenderer.sprite = wanjianSprites[8]; // F9 肃杀静止
            yield return new WaitForSeconds(0.10f);

            if (spriteRenderer != null) spriteRenderer.sprite = wanjianSprites[9]; // F10 晶核共鸣
            yield return new WaitForSeconds(0.08f);

            if (spriteRenderer != null) spriteRenderer.sprite = wanjianSprites[10]; // F11 临界超载 (时空顿帧)
            Time.timeScale = 0.25f;
            yield return new WaitForSecondsRealtime(0.08f);
            Time.timeScale = 1.0f;

            if (spriteRenderer != null) spriteRenderer.sprite = wanjianSprites[11]; // F12 漫天爆灭
            PokongciBloomFX.Instance.TriggerCameraShake(0.35f, 0.16f);
            yield return new WaitForSeconds(0.10f);

            // 阶段四：星屑沉降与拂袖入鞘 (F13 ~ F16)
            float[] recoveryDurations = new float[] { 0.08f, 0.08f, 0.10f, 0.14f };
            for (int i = 12; i < 16; i++)
            {
                if (spriteRenderer != null) spriteRenderer.sprite = wanjianSprites[i];
                yield return new WaitForSeconds(recoveryDurations[i - 12]);
            }
        }
        else
        {
            yield return new WaitForSeconds(0.5f);
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

    IEnumerator WanjianBloomRoutine()
    {
        isSkillPlaying = true;
        currentActionName = "【剑意绽放·终极绝学】万剑归宗·极 · 太虚绝仙剑界 (QF-6E)";
        swordIntent = 0; // 消耗 5 阶满额剑意

        if (wanjianBloomSprites == null || wanjianBloomSprites.Length < 16 || wanjianBloomSprites[0] == null)
        {
            LoadWanjianBloomSprites();
        }
        if (fallingSwordBloom45Sprite == null) LoadWanjianProjectiles();

        if (animator != null) animator.enabled = false;
        bool origFlip = spriteRenderer != null && spriteRenderer.flipX;
        float faceDir = origFlip ? -1f : 1f;

        if (wanjianBloomSprites != null && wanjianBloomSprites.Length >= 16 && wanjianBloomSprites[0] != null)
        {
            if (spriteRenderer != null) spriteRenderer.color = new Color(0.85f, 1f, 1f, 1f);

            // 阶段一：六翼初展与太虚天门 (F1 ~ F4)
            float[] startupDurations = new float[] { 0.09f, 0.09f, 0.10f, 0.12f };
            for (int i = 0; i < 3; i++)
            {
                if (spriteRenderer != null) spriteRenderer.sprite = wanjianBloomSprites[i];
                yield return new WaitForSeconds(startupDurations[i]);
            }

            // F4 神目锁界 · 0.15s 绝对时空停顿
            if (spriteRenderer != null) spriteRenderer.sprite = wanjianBloomSprites[3];
            Time.timeScale = 0.15f;
            PokongciBloomFX.Instance.TriggerCameraShake(0.20f, 0.08f);
            yield return new WaitForSecondsRealtime(0.12f);
            Time.timeScale = 1.0f;

            // 阶段二：神陨圣裁与巍峨玄峰 (F5 ~ F8)
            float[] barrageDurations = new float[] { 0.08f, 0.08f, 0.08f, 0.08f };
            for (int i = 4; i < 8; i++)
            {
                if (spriteRenderer != null) spriteRenderer.sprite = wanjianBloomSprites[i];
                StartCoroutine(SpawnFallingSwordRain(true, 6, faceDir));
                PokongciBloomFX.Instance.TriggerCameraShake(0.25f, 0.10f);
                yield return new WaitForSeconds(barrageDurations[i - 4]);
            }

            // 阶段三：引力黑洞坍缩与太虚十字大核爆 (F9 ~ F12)
            if (spriteRenderer != null) spriteRenderer.sprite = wanjianBloomSprites[8]; // F9 虚空黑洞
            yield return new WaitForSeconds(0.10f);

            if (spriteRenderer != null) spriteRenderer.sprite = wanjianBloomSprites[9]; // F10 临界逆转 + 巨大太虚主剑轰顶贯穿
            StartCoroutine(SpawnGrandDivineSword(faceDir));
            yield return new WaitForSeconds(0.08f);

            if (spriteRenderer != null) spriteRenderer.sprite = wanjianBloomSprites[10]; // F11 十字圣爆
            PokongciBloomFX.Instance.TriggerCameraShake(0.60f, 0.28f);
            Time.timeScale = 0.20f;
            yield return new WaitForSecondsRealtime(0.15f);
            Time.timeScale = 1.0f;

            if (spriteRenderer != null) spriteRenderer.sprite = wanjianBloomSprites[11]; // F12 双重音速激波
            yield return new WaitForSeconds(0.10f);

            // 阶段四：剑仙真身与踏莲入鞘 (F13 ~ F16)
            float[] recoveryDurations = new float[] { 0.09f, 0.09f, 0.10f, 0.16f };
            for (int i = 12; i < 16; i++)
            {
                if (spriteRenderer != null) spriteRenderer.sprite = wanjianBloomSprites[i];
                yield return new WaitForSeconds(recoveryDurations[i - 12]);
            }
        }
        else
        {
            yield return new WaitForSeconds(0.5f);
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

    IEnumerator SpawnFallingSwordRain(bool isBloom, int count, float faceDir)
    {
        Sprite swordSp = isBloom ? fallingSwordBloom45Sprite : fallingSwordNormal45Sprite;
        if (swordSp == null) yield break;

        for (int i = 0; i < count; i++)
        {
            StartCoroutine(SpawnSingleFallingSword(isBloom, swordSp, faceDir, i));
        }
    }

    IEnumerator SpawnSingleFallingSword(bool isBloom, Sprite swordSp, float faceDir, int swordIndex)
    {
        if (swordSp == null) yield break;

        // 微时间差错开生成，形成如狂风骤雨般连绵不绝的密布飞剑暴雨
        if (swordIndex > 0)
        {
            yield return new WaitForSeconds(Random.Range(0.015f, 0.045f) * swordIndex);
        }

        Vector3 startPos;
        Vector3 targetPos;

        if (!isBloom)
        {
            // === 常态万剑归宗 (QF-6)：前向 45°~60° 斜角破空呼啸飞剑 (Slanted Forward Meteor Barrage) ===
            // 飞剑从角色后上方/九天云阙呼啸破空，以 45°~60° 凌厉斜角猛烈插向角色面朝的前方战区
            float targetDistAhead = Random.Range(1.2f, 7.2f);
            float targetX = transform.position.x + targetDistAhead * faceDir;
            float skyY = Random.Range(5.2f, 7.5f);
            // 倾角：X 坐标往后方 (反方向) 偏移 3.2m ~ 4.8m，形成气势磅礴的斜向俯冲势
            float slantX = Random.Range(3.2f, 4.8f) * faceDir;

            startPos = new Vector3(targetX - slantX, transform.position.y + skyY, 0f);
            targetPos = new Vector3(targetX, groundY, 0f);
        }
        else
        {
            // === 剑意绽放·极 (QF-6E)：太虚绝仙剑界 · 天穹环形聚拢阵 (Celestial Convergence Dome) ===
            // 完美还原图三概念图：九天雷云八卦剑门，飞剑呈天穹穹顶扇形向前方战场核心聚拢穿插
            float targetDistAhead = Random.Range(0.8f, 7.5f);
            float targetX = transform.position.x + targetDistAhead * faceDir;

            // 天穹阵列宽幅覆盖 [-6m, +7.5m]
            float skySpread = Random.Range(-5.5f, 7.5f) * faceDir;
            float skyY = Random.Range(5.5f, 8.2f);
            startPos = new Vector3(transform.position.x + skySpread, transform.position.y + skyY, 0f);
            targetPos = new Vector3(targetX, groundY, 0f);
        }

        Vector3 travelDir = (targetPos - startPos).normalized;
        // 计算飞行方向角 (度数)
        float travelAngle = Mathf.Atan2(travelDir.y, travelDir.x) * Mathf.Rad2Deg;
        // 原生精灵素材剑尖朝正下方 (-90度)，旋转角为 travelAngle + 90
        Quaternion swordRotation = Quaternion.Euler(0f, 0f, travelAngle + 90f);

        GameObject swordObj = new GameObject("FallingSword_FX");
        swordObj.transform.position = startPos;
        swordObj.transform.rotation = swordRotation;

        SpriteRenderer sr = swordObj.AddComponent<SpriteRenderer>();
        sr.sprite = swordSp;
        sr.sortingOrder = 10;

        float scaleFactor = isBloom ? Random.Range(0.38f, 0.46f) : Random.Range(0.30f, 0.38f);
        swordObj.transform.localScale = new Vector3(scaleFactor, scaleFactor, 1f);

        if (isBloom)
        {
            sr.color = new Color(1f, 0.96f, 0.75f, 1f);
        }

        // 高速贯空 (24 ~ 35 m/s)
        float speed = isBloom ? Random.Range(28f, 38f) : Random.Range(22f, 30f);
        float totalDist = Vector3.Distance(startPos, targetPos);
        float duration = totalDist / speed;

        float elapsed = 0f;
        while (elapsed < duration)
        {
            elapsed += Time.deltaTime;
            float t = Mathf.Clamp01(elapsed / duration);
            if (swordObj != null)
            {
                swordObj.transform.position = Vector3.Lerp(startPos, targetPos, t);
            }
            yield return null;
        }

        // 贯穿入地阶段：剑尖钉入地面，保持冲击斜角微震
        if (swordObj != null)
        {
            swordObj.transform.position = targetPos;
            PokongciBloomFX.Instance.TriggerCameraShake(isBloom ? 0.08f : 0.04f, 0.04f);

            // 剑尖入石微颤 0.18s ~ 0.28s
            float stickDuration = Random.Range(0.18f, 0.28f);
            float stickElapsed = 0f;
            Vector3 stickBase = targetPos;
            while (stickElapsed < stickDuration && swordObj != null)
            {
                stickElapsed += Time.deltaTime;
                float jitter = Mathf.Sin(stickElapsed * 60f) * 0.02f;
                swordObj.transform.position = stickBase + new Vector3(jitter, jitter * 0.5f, 0f);
                yield return null;
            }

            // 剑气消散渐隐 0.20s
            float fadeDuration = 0.20f;
            float fadeElapsed = 0f;
            while (fadeElapsed < fadeDuration && swordObj != null)
            {
                fadeElapsed += Time.deltaTime;
                if (sr != null)
                {
                    Color c = sr.color;
                    c.a = 1.0f - (fadeElapsed / fadeDuration);
                    sr.color = c;
                }
                yield return null;
            }
            Destroy(swordObj);
        }
    }

    IEnumerator SpawnGrandDivineSword(float faceDir)
    {
        Sprite swordSp = fallingSwordBloom45Sprite;
        if (swordSp == null) yield break;

        Vector3 targetPos = new Vector3(transform.position.x + 3.2f * faceDir, groundY, 0f);
        Vector3 startPos = new Vector3(targetPos.x - 2.2f * faceDir, transform.position.y + 8.5f, 0f);

        Vector3 travelDir = (targetPos - startPos).normalized;
        float travelAngle = Mathf.Atan2(travelDir.y, travelDir.x) * Mathf.Rad2Deg;
        Quaternion swordRotation = Quaternion.Euler(0f, 0f, travelAngle + 90f);

        GameObject giantSword = new GameObject("GrandDivineSword_FX");
        giantSword.transform.position = startPos;
        giantSword.transform.rotation = swordRotation;
        giantSword.transform.localScale = new Vector3(0.95f, 0.95f, 1f); // 巨大主剑

        SpriteRenderer sr = giantSword.AddComponent<SpriteRenderer>();
        sr.sprite = swordSp;
        sr.sortingOrder = 12;
        sr.color = new Color(1f, 1f, 0.85f, 1f);

        float speed = 36f;
        float dur = Vector3.Distance(startPos, targetPos) / speed;
        float el = 0f;
        while (el < dur && giantSword != null)
        {
            el += Time.deltaTime;
            giantSword.transform.position = Vector3.Lerp(startPos, targetPos, el / dur);
            yield return null;
        }

        if (giantSword != null)
        {
            giantSword.transform.position = targetPos;
            PokongciBloomFX.Instance.TriggerCameraShake(0.55f, 0.25f);

            yield return new WaitForSeconds(0.35f);

            float fade = 0.25f;
            while (fade > 0f && giantSword != null)
            {
                fade -= Time.deltaTime;
                if (sr != null)
                {
                    Color c = sr.color;
                    c.a = fade / 0.25f;
                    sr.color = c;
                }
                yield return null;
            }
            Destroy(giantSword);
        }
    }

    private Vector2 guiScrollPos = Vector2.zero;

    void OnGUI()
    {
        // 仅在独立预览模式下绘制操控面板
        if (combat != null) return;

        float panelHeight = Mathf.Min(Screen.height - 20, 880);
        GUILayout.BeginArea(new Rect(15, 10, 480, panelHeight), GUI.skin.box);
        guiScrollPos = GUILayout.BeginScrollView(guiScrollPos);

        GUILayout.Label("<b><size=15>【刀影江湖 · 青锋动作与技能预览台】</size></b>");
        GUILayout.Space(4);
        GUILayout.Label($"<b>当前动作：</b><color=#00ff88>{currentActionName}</color>");
        GUILayout.Label($"<b>剑意状态：</b>[ <color=#00e1ff>{new string('★', swordIntent)}{new string('☆', 5 - swordIntent)}</color> ({swordIntent}/5阶) ]  " +
                        $"<color={(isBloomActive ? "#ffff00" : "#aaaaaa")}><b>{(isBloomActive ? "【剑意澄澈·可绽放】" : "蓄力中")}</b></color>");

        string blockStatus = IsStunned 
            ? "<b><color=#ff3333>【⚠️ 弹刀破防僵直中！】</color></b>" 
            : (IsBlocking ? "<color=#00ff88>【架势保持中】</color>" : "未格挡");
        string effColor = blockEfficiency > 0.7f ? "#00ff88" : (blockEfficiency > 0.45f ? "#ffcc00" : "#ff3333");
        string strainColor = guardStrain < 50f ? "#00e1ff" : (guardStrain < 80f ? "#ff9900" : "#ff2222");

        GUILayout.Label($"<b>接地：</b>{(isGrounded ? "地面" : "空中")} | <b>格挡状态：</b>{blockStatus}");
        GUILayout.Label($"<b>格挡效能：</b><color={effColor}><b>{Mathf.RoundToInt(blockEfficiency * 100)}%</b></color> (维持时间:{blockHoldDuration:F2}s) | " +
                        $"<b>架势负荷：</b><color={strainColor}><b>{Mathf.RoundToInt(guardStrain)}/100</b></color>" + (guardStrain >= 80f ? " <color=red><b>[濒临破防]</b></color>" : ""));

        if (IsStunned)
        {
            GUILayout.Label($"<color=#ff3333><b>>>> 破防僵直剩余：{stunTimer:F2} 秒 (全动作封锁无法行动) <<<</b></color>");
        }
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
        GUILayout.Label("<b>--- 技能3：一剑霜寒 (破防霜线 / 绝对霜冻·冰魄玄峰 I) ---</b>");
        GUILayout.BeginHorizontal();
        GUI.color = new Color(0.45f, 0.85f, 1f);
        if (GUILayout.Button("一剑霜寒·常态 (8阶段破防霜线)", GUILayout.Height(30)))
        {
            StartCoroutine(YijianshuanghanRoutine(false));
        }
        GUI.color = new Color(0.3f, 1f, 1f);
        if (GUILayout.Button("★ 极·冰魄玄峰 (绝对霜冻·万晶爆)", GUILayout.Height(30)))
        {
            TriggerYijianshuanghanBloom();
        }
        GUI.color = Color.white;
        GUILayout.EndHorizontal();

        GUILayout.Space(6);
        GUILayout.Label("<b>--- 技能4：引剑诀 · 流光溯影 (天外飞剑贯通归鞘 R/P) ---</b>");
        GUILayout.BeginHorizontal();
        GUI.color = new Color(0.2f, 1f, 0.85f);
        if (GUILayout.Button("常态引剑诀 (飞剑贯通+强力合刃)", GUILayout.Height(30)))
        {
            if (yinjianjueSprites == null || yinjianjueSprites.Length < 8 || yinjianjueSprites[0] == null)
            {
                LoadYinjianjueSprites();
            }
            StartCoroutine(YinjianjueRoutine());
        }
        GUI.color = new Color(1f, 0.85f, 0.2f);
        if (GUILayout.Button("★ 极·引剑诀 (混元归渊·冰破乾坤)", GUILayout.Height(30)))
        {
            TriggerYinjianjueBloom();
        }
        GUI.color = Color.white;
        GUILayout.EndHorizontal();

        GUILayout.Space(6);
        GUILayout.Label("<b>--- 技能5：以剑御气 · 苍龙玄天钟 / 万仞诛魔剑界 (长按维持护盾 G / Shift+F) ---</b>");
        GUILayout.BeginHorizontal();
        if (isYuqiShieldActive || isYuqiBloomShieldActive)
        {
            GUI.color = new Color(1f, 0.45f, 0.45f);
            if (GUILayout.Button("松开护盾 (完成剩下动作/反震)", GUILayout.Height(30)))
            {
                isYuqiFromGui = false;
            }
            GUI.color = new Color(0.35f, 1f, 0.85f);
            float currentAbsorbed = isYuqiBloomShieldActive ? yuqiBloomAbsorbedDamage : yuqiAbsorbedDamage;
            float currentMax = isYuqiBloomShieldActive ? maxYuqiBloomShield : maxYuqiShield;
            if (GUILayout.Button($"模拟受击 (+25) [{Mathf.RoundToInt(currentAbsorbed)}/{Mathf.RoundToInt(currentMax)}]", GUILayout.Height(30)))
            {
                AbsorbYuqiHit(25f, isYuqiBloomShieldActive);
            }
        }
        else
        {
            GUI.color = new Color(0.2f, 0.9f, 1f);
            if (GUILayout.Button("常态以剑御气 (按住维持护盾)", GUILayout.Height(30)))
            {
                if (yijianyuqiSprites == null || yijianyuqiSprites.Length < 16 || yijianyuqiSprites[0] == null)
                {
                    LoadYijianyuqiSprites();
                }
                TriggerYijianyuqi(true);
            }
            GUI.color = new Color(1f, 0.75f, 0.2f);
            if (GUILayout.Button("★ 极·以剑御气 (按住维持金刚剑界)", GUILayout.Height(30)))
            {
                TriggerYijianyuqiBloom(true);
            }
        }
        GUI.color = Color.white;
        GUILayout.EndHorizontal();

        GUILayout.Space(6);
        GUILayout.Label("<b>--- 技能6：万剑归宗 · 终极绝学 (全屏飞剑暴雨倾天 / 太虚绝仙剑界 Y/V) ---</b>");
        GUILayout.BeginHorizontal();
        GUI.color = new Color(0.2f, 0.95f, 1f);
        if (GUILayout.Button("常态万剑归宗 (36柄流星剑雨+超新星爆 Y)", GUILayout.Height(30)))
        {
            TriggerWanjian();
        }
        GUI.color = new Color(1f, 0.85f, 0.1f);
        if (GUILayout.Button("★ 极·万剑归宗 (太虚天门+冰魄玄峰+时停大核爆 V)", GUILayout.Height(30)))
        {
            TriggerWanjianBloom();
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
        GUILayout.Label("<b>--- 防守、架势与破防测试 ---</b>");
        GUILayout.BeginHorizontal();
        if (GUILayout.Button(IsBlocking ? "松开格挡(F)" : "格挡保持(F)"))
        {
            if (IsBlocking) ExitBlock();
            else PerformBlock(true);
        }
        if (GUILayout.Button("模拟受击(G/H)")) TriggerBlockHit();
        if (GUILayout.Button("完美弹反(T)")) TriggerParrySuccess();
        GUI.color = new Color(1f, 0.45f, 0.45f);
        if (GUILayout.Button("测试弹刀破防")) TriggerGuardBreak();
        GUI.color = Color.white;
        if (GUILayout.Button("闪避(Space)")) StartDodge();
        GUILayout.EndHorizontal();

        GUILayout.Space(6);
        GUILayout.Label("<color=#cccccc><size=11>按键提示：长按 F 维持格挡（随时间衰减）；长按 G 或 Shift+F 维持以剑御气（无时间衰减，全额吸收伤害，松手或超限释放反震）\n" +
                        "按 H 模拟受击 | 按 T 完美弹反 | Space 闪避 | J 轻击三连 | K 重刺 | Q/U 破空刺 | E/O 回风舞 | I 霜寒 | R/P 引剑 | Y/V 万剑归宗</size></color>");

        GUILayout.EndScrollView();
        GUILayout.EndArea();
    }
}
