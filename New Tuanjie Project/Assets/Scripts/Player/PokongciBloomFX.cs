using System.Collections;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// 剑意绽放·极破空刺 专属电影级视觉特效系统 (Pokongci Bloom VFX System):
/// 1. 聚势期：四灵青光飞剑同轴螺旋环绕 + 刚体青金护体盾
/// 2. 突进期：长 4.5 米天崩级青白裂空巨锥 + 5 重流光水墨残影 (Ghost Trails)
/// 3. 穿透期：全屏 6f 时空停滞 (Chrono Hitstop) + 镜头暴震 (Camera Trauma Shake)
/// 4. 留痕期：贯穿全径的虚空空间裂隙 (Spatial Void Rift) + 4 米玄冰霜痕地表结界
/// 5. 爆发期：穿透敌后三度连环断空墨爆 (Triple Ink Detonations) + 十字裂空星芒 + 环形冲击波
/// 全部特效元素采用程序化高清材质自动构建，即插即用，零依赖，视觉反差极为强烈！
/// </summary>
public class PokongciBloomFX : MonoBehaviour
{
    private static PokongciBloomFX _instance;
    public static PokongciBloomFX Instance
    {
        get
        {
            if (_instance == null)
            {
                GameObject go = new GameObject("[PokongciBloomFX_System]");
                _instance = go.AddComponent<PokongciBloomFX>();
                DontDestroyOnLoad(go);
            }
            return _instance;
        }
    }

    // 缓存程序化生成的 Sprite 贴图
    private Sprite starburstSprite;
    private Sprite shockwaveSprite;
    private Sprite voidConeSprite;
    private Sprite flyingSwordSprite;
    private Sprite frostDecalSprite;
    private Sprite spatialRiftSprite;
    private Sprite particleDotSprite;
    private Sprite crescentSlashSprite;
    private Material additiveMat;

    void Awake()
    {
        if (_instance == null) _instance = this;
        InitProceduralSprites();
    }

    private void InitProceduralSprites()
    {
        // 1. 十字裂空星芒 (Starburst)
        starburstSprite = CreateCrossStarburst(256, 256);

        // 2. 环形水墨冲击波 (Shockwave Ring)
        shockwaveSprite = CreateShockwaveRing(256, 256);

        // 3. 超巨型裂空光锥 (Colossal Void Cone)
        voidConeSprite = CreateVoidCone(512, 180);

        // 4. 悬浮青灵飞剑 (Flying Sword)
        flyingSwordSprite = CreateFlyingSword(200, 48);

        // 5. 地表冰霜裂痕 (Frost Decal)
        frostDecalSprite = CreateFrostDecal(512, 64);

        // 6. 空间裂痕 (Spatial Rift)
        spatialRiftSprite = CreateSpatialRift(512, 48);

        // 7. 发光星尘粒子
                particleDotSprite = CreateParticleDot(32, 32);

        // 8. 狂草残月剑芒 (Crescent Blade Slash)
        crescentSlashSprite = CreateCrescentSlash(512, 256);

        // 查找或创建通用材质
        Shader s = Shader.Find("Sprites/Default");
        if (s != null) additiveMat = new Material(s);
    }

    /// <summary>
    /// 触发常态破空刺错身特效（细青白激光线 + 2重残影 + 敌后延时单次破空血墨爆）
    /// </summary>
    public void PlayNormalPokongciFX(Transform caster, bool flipX, Vector3 startPos, Vector3 endPos, Sprite casterSprite)
    {
        StartCoroutine(NormalSequenceRoutine(caster, flipX, startPos, endPos, casterSprite));
    }

    private IEnumerator NormalSequenceRoutine(Transform caster, bool flipX, Vector3 startPos, Vector3 endPos, Sprite casterSprite)
    {
        float dir = flipX ? -1f : 1f;

        // 1. 2 道轻盈水墨残影
        SpawnGhostShadow(Vector3.Lerp(startPos, endPos, 0.35f), casterSprite, flipX, 0.4f);
        yield return new WaitForSeconds(0.035f);
        SpawnGhostShadow(Vector3.Lerp(startPos, endPos, 0.70f), casterSprite, flipX, 0.8f);

        // 2. 极细平切青白穿透光刃 (扁平锐利如激光)
        GameObject beamGo = new GameObject("VFX_NormalLaserBeam");
        SpriteRenderer beamSr = beamGo.AddComponent<SpriteRenderer>();
        beamSr.sprite = voidConeSprite;
        beamSr.color = new Color(0.3f, 0.95f, 1f, 0.85f);
        beamSr.sortingOrder = 16;
        beamGo.transform.position = (startPos + endPos) * 0.5f + new Vector3(0, 0.35f, 0);
        beamGo.transform.localScale = new Vector3(dir * 0.85f, 0.25f, 1f); // 极其扁平切面
        StartCoroutine(FadeAndDestroy(beamGo, 0.15f));

        // 3. 错身到达敌后轻微顿挫
        TriggerCameraShake(0.12f, 0.08f);

        // 4. 慢半拍！第 0.06 秒敌人身上爆开单次清脆裂体墨爆
        yield return new WaitForSeconds(0.06f);
        Vector3 midEnemyPos = Vector3.Lerp(startPos, endPos, 0.55f) + new Vector3(0, 0.35f, 0);
        SpawnDetonationBurst(midEnemyPos, 1);
        TriggerCameraShake(0.18f, 0.10f);
    }

    /// <summary>
    /// 触发回风舞旋风剑轮与风暴解围特效 (QF-2 / QF-2E)
    /// </summary>
    public void PlayHuifengwuFX(Transform caster, bool isBloom)
    {
        StartCoroutine(HuifengwuRoutine(caster, isBloom));
    }

    private IEnumerator HuifengwuRoutine(Transform caster, bool isBloom)
    {
        Vector3 center = caster.position + new Vector3(0, 0.55f, 0);
        float radiusScale = isBloom ? 1.5f : 1.0f;

        // 阶段 1：剑尖蓄势寒芒 (F1)
        GameObject glintF1 = new GameObject("VFX_SwordGlint_F1");
        glintF1.transform.position = center + new Vector3(0.35f, -0.2f, 0);
        glintF1.transform.localScale = Vector3.one * (0.8f * radiusScale);
        SpriteRenderer glintSr = glintF1.AddComponent<SpriteRenderer>();
        glintSr.sprite = starburstSprite;
        glintSr.color = Color.white;
        glintSr.sortingOrder = 22;
        StartCoroutine(FadeAndDestroy(glintF1, 0.12f));

        yield return new WaitForSeconds(0.06f);

        // 阶段 2：初斩残月剑幕 (F3) —— 凌厉横斩月牙刀芒，呼啸破空！
        SpawnCrescentSlash(center, 0f, new Vector2(2.4f * radiusScale, 1.4f * radiusScale),
            isBloom ? new Color(0.3f, 1f, 1f, 0.95f) : new Color(0.5f, 0.95f, 1f, 0.9f), 0.16f);
        SpawnSwordStar(center + new Vector3(0.9f * radiusScale, 0, 0), 1.2f * radiusScale, 0.14f);
        SpawnSlashSparks(center, 14, 1.2f * radiusScale, isBloom);
        TriggerCameraShake(isBloom ? 0.15f : 0.08f, 0.06f);

        yield return new WaitForSeconds(isBloom ? 0.08f : 0.10f);

        // 阶段 3：双重残月交错绝杀 (F5) —— 水平与斜切双道斩芒暴烈交叠！
        SpawnCrescentSlash(center, -8f, new Vector2(2.6f * radiusScale, 1.5f * radiusScale),
            Color.white, 0.18f);
        SpawnCrescentSlash(center, 38f, new Vector2(2.3f * radiusScale, 1.4f * radiusScale),
            isBloom ? new Color(1f, 0.92f, 0.35f, 0.95f) : new Color(0.3f, 1f, 0.95f, 0.9f), 0.18f);
        
        // 交错核心爆鸣星芒
        SpawnSwordStar(center + new Vector3(0.6f * radiusScale, 0.1f, 0), 1.6f * radiusScale, 0.18f);
        SpawnSlashSparks(center, 24, 1.6f * radiusScale, isBloom);
        TriggerCameraShake(isBloom ? 0.28f : 0.15f, 0.10f);

        if (isBloom)
        {
            // 强化青鸾风暴：额外 3 道高速残月回旋绞杀连击
            for (int b = 0; b < 3; b++)
            {
                yield return new WaitForSeconds(0.05f);
                float angle = -30f + b * 45f;
                SpawnCrescentSlash(center, angle, new Vector2(2.5f * radiusScale, 1.3f * radiusScale),
                    new Color(0.4f, 1f, 1f, 0.9f), 0.14f);
                SpawnSlashSparks(center, 12, 1.4f * radiusScale, true);
                TriggerCameraShake(0.18f, 0.04f);
            }
        }

        yield return new WaitForSeconds(0.08f);

        // 阶段 4：侧步插剑定地裂痕 (F6) —— 剑尖重插地面，锐利剑劲左右平射！
        Vector3 groundTip = caster.position + new Vector3(0.35f, 0.02f, 0);
        GameObject groundCrack = new GameObject("VFX_GroundSwordShock");
        groundCrack.transform.position = groundTip;
        groundCrack.transform.localScale = new Vector3(2.5f * radiusScale, 0.35f, 1f);
        SpriteRenderer gcSr = groundCrack.AddComponent<SpriteRenderer>();
        gcSr.sprite = frostDecalSprite;
        gcSr.color = isBloom ? new Color(0.3f, 1f, 1f, 0.9f) : new Color(0.6f, 0.95f, 1f, 0.8f);
        gcSr.sortingOrder = 15;
        StartCoroutine(FadeAndDestroy(groundCrack, 0.35f));

        // 落地星火
        SpawnSwordStar(groundTip, 1.0f * radiusScale, 0.15f);
    }

    private void SpawnCrescentSlash(Vector3 pos, float angleDeg, Vector2 scale, Color color, float life)
    {
        GameObject slash = new GameObject("VFX_CrescentSlash");
        slash.transform.position = pos;
        slash.transform.rotation = Quaternion.Euler(0, 0, angleDeg);
        slash.transform.localScale = scale * 0.7f;
        SpriteRenderer sr = slash.AddComponent<SpriteRenderer>();
        sr.sprite = crescentSlashSprite != null ? crescentSlashSprite : voidConeSprite;
        sr.color = color;
        sr.sortingOrder = 20;

        StartCoroutine(AnimateCrescentSlash(slash, scale, life));
    }

    private IEnumerator AnimateCrescentSlash(GameObject slash, Vector2 targetScale, float life)
    {
        float elapsed = 0f;
        Vector2 startScale = targetScale * 0.75f;
        SpriteRenderer sr = slash.GetComponent<SpriteRenderer>();
        Color startCol = sr.color;

        while (elapsed < life)
        {
            elapsed += Time.deltaTime;
            float t = elapsed / life;
            slash.transform.localScale = Vector2.Lerp(startScale, targetScale * 1.15f, Mathf.Sqrt(t));
            sr.color = new Color(startCol.r, startCol.g, startCol.b, Mathf.Lerp(startCol.a, 0f, t * t));
            yield return null;
        }
        Destroy(slash);
    }

    private void SpawnSwordStar(Vector3 pos, float scale, float life)
    {
        GameObject star = new GameObject("VFX_SwordStar");
        star.transform.position = pos;
        star.transform.localScale = Vector3.one * scale;
        SpriteRenderer sr = star.AddComponent<SpriteRenderer>();
        sr.sprite = starburstSprite;
        sr.color = Color.white;
        sr.sortingOrder = 22;
        StartCoroutine(FadeAndDestroy(star, life));
    }

    private void SpawnSlashSparks(Vector3 center, int count, float radius, bool isBloom)
    {
        for (int i = 0; i < count; i++)
        {
            GameObject spark = new GameObject("VFX_SlashSpark");
            spark.transform.position = center + (Vector3)(Random.insideUnitCircle * 0.35f);
            spark.transform.localScale = Vector3.one * Random.Range(0.4f, 0.9f);
            SpriteRenderer sr = spark.AddComponent<SpriteRenderer>();
            sr.sprite = particleDotSprite;
            sr.color = isBloom && Random.value > 0.5f
                ? new Color(1f, 0.95f, 0.4f, 1f)
                : (Random.value > 0.4f ? Color.white : new Color(0.2f, 0.95f, 1f, 1f));
            sr.sortingOrder = 21;

            Vector2 dir = Random.insideUnitCircle.normalized;
            float spd = Random.Range(3.5f, 7.5f);
            StartCoroutine(AnimateSpark(spark, dir * spd, Random.Range(0.12f, 0.22f)));
        }
    }

    private IEnumerator AnimateSpark(GameObject spark, Vector2 vel, float life)
    {
        float elapsed = 0f;
        SpriteRenderer sr = spark.GetComponent<SpriteRenderer>();
        Color startCol = sr.color;

        while (elapsed < life)
        {
            elapsed += Time.deltaTime;
            spark.transform.position += (Vector3)(vel * Time.deltaTime);
            float t = elapsed / life;
            sr.color = new Color(startCol.r, startCol.g, startCol.b, 1f - t);
            yield return null;
        }
        Destroy(spark);
    }

        public void PlayBloomEffect(Transform caster, bool flipX, Vector3 startPos, Vector3 endPos, Sprite casterSprite)
    {
        StartCoroutine(BloomSequenceRoutine(caster, flipX, startPos, endPos, casterSprite));
    }

    private IEnumerator BloomSequenceRoutine(Transform caster, bool flipX, Vector3 startPos, Vector3 endPos, Sprite casterSprite)
    {
        float dir = flipX ? -1f : 1f;
        Vector3 swordHandOffset = new Vector3(dir * 0.45f, 0.4f, 0f);

        // ==========================================
        // 【第一阶段：聚势 · 四灵飞剑环绕 + 刚体青金护体】
        // ==========================================
        List<GameObject> swords = new List<GameObject>();
        for (int i = 0; i < 4; i++)
        {
            GameObject sw = new GameObject($"OrbitSword_{i}");
            SpriteRenderer sr = sw.AddComponent<SpriteRenderer>();
            sr.sprite = flyingSwordSprite;
            sr.color = new Color(0.2f, 0.95f, 1f, 0.9f);
            sr.sortingOrder = 15;
            swords.Add(sw);
        }

        float gatherTime = 0.16f;
        float elapsed = 0f;
        while (elapsed < gatherTime)
        {
            elapsed += Time.deltaTime;
            float t = elapsed / gatherTime;
            Vector3 center = caster.position + swordHandOffset;
            float angleBase = elapsed * 1080f; // 超高速旋转

            for (int i = 0; i < 4; i++)
            {
                float ang = (angleBase + i * 90f) * Mathf.Deg2Rad;
                float radius = Mathf.Lerp(0.9f, 0.35f, t);
                swords[i].transform.position = center + new Vector3(Mathf.Cos(ang) * radius * 0.5f, Mathf.Sin(ang) * radius, 0f);
                float rotZ = (angleBase + i * 90f);
                if (flipX) rotZ += 180f;
                swords[i].transform.rotation = Quaternion.Euler(0, 0, rotZ);
                swords[i].transform.localScale = Vector3.one * Mathf.Lerp(0.8f, 1.2f, t);
            }
            yield return null;
        }

        // ==========================================
        // 【第二阶段：瞬透 · 天崩巨锥 + 5重流光水墨残影】
        // ==========================================
        // 四柄飞剑如螺旋钻头先行射出并淡出
        for (int i = 0; i < 4; i++)
        {
            StartCoroutine(FadeAndDestroy(swords[i], 0.12f));
        }

        // 生成超巨型裂空光锥 (Void Cone)
        GameObject coneGo = new GameObject("VFX_VoidCone");
        SpriteRenderer coneSr = coneGo.AddComponent<SpriteRenderer>();
        coneSr.sprite = voidConeSprite;
        coneSr.color = new Color(1f, 1f, 1f, 1f);
        coneSr.sortingOrder = 18;
        coneGo.transform.position = caster.position + swordHandOffset + new Vector3(dir * 1.8f, 0f, 0f);
        coneGo.transform.localScale = new Vector3(dir * 1.5f, 1.4f, 1f);
        StartCoroutine(AnimateCone(coneGo, coneSr, dir));

        // 伴随位移释放 5 道水墨流光残影
        float dashDuration = 0.18f;
        float dashTimer = 0f;
        int shadowCount = 5;
        for (int s = 0; s < shadowCount; s++)
        {
            float ratio = (float)s / (shadowCount - 1);
            Vector3 shadowPos = Vector3.Lerp(startPos, endPos, ratio);
            SpawnGhostShadow(shadowPos, casterSprite, flipX, ratio);
            yield return new WaitForSeconds(dashDuration / shadowCount);
        }

        // ==========================================
        // 【第三阶段：贯穿 · 时空停滞 + 镜头暴震】
        // ==========================================
        // 生成永久性空间裂缝与地面冰霜霜痕
        GameObject riftGo = new GameObject("VFX_SpatialRift");
        SpriteRenderer riftSr = riftGo.AddComponent<SpriteRenderer>();
        riftSr.sprite = spatialRiftSprite;
        riftSr.color = new Color(0.2f, 0.85f, 1f, 0.95f);
        riftSr.sortingOrder = 14;
        Vector3 midPath = (startPos + endPos) * 0.5f + new Vector3(0, 0.35f, 0);
        riftGo.transform.position = midPath;
        riftGo.transform.localScale = new Vector3(dir * 1.1f, 1.2f, 1f);

        // 地面冰霜结界
        GameObject frostGo = new GameObject("VFX_FrostDecal");
        SpriteRenderer frostSr = frostGo.AddComponent<SpriteRenderer>();
        frostSr.sprite = frostDecalSprite;
        frostSr.color = new Color(0.6f, 0.95f, 1f, 0.85f);
        frostSr.sortingOrder = 5;
        frostGo.transform.position = new Vector3(midPath.x, startPos.y - 0.05f, 0);
        frostGo.transform.localScale = new Vector3(1.2f, 1f, 1f);
        StartCoroutine(FadeAndDestroy(frostGo, 2.5f));

        // 强力全屏时空停滞
        TriggerCameraShake(0.35f, 0.15f);
        Time.timeScale = 0.15f;
        yield return new WaitForSecondsRealtime(0.08f);
        Time.timeScale = 1.0f;

        // ==========================================
        // 【第四阶段：引爆 · 三度连环断空墨爆】
        // ==========================================
        yield return new WaitForSeconds(0.05f);

        // 穿透轨迹上依次三段爆破 (25%, 60%, 95%)
        float[] burstRatios = new float[] { 0.25f, 0.60f, 0.95f };
        for (int b = 0; b < 3; b++)
        {
            Vector3 burstPos = Vector3.Lerp(startPos, endPos, burstRatios[b]) + new Vector3(0, 0.4f, 0);
            SpawnDetonationBurst(burstPos, b + 1);
            TriggerCameraShake(0.25f + b * 0.1f, 0.12f);
            yield return new WaitForSeconds(0.06f);
        }

        // 空间裂缝淡化消除
        StartCoroutine(FadeAndDestroy(riftGo, 0.4f));
    }

    /// <summary>
    /// 生成流光水墨残影
    /// </summary>
    private void SpawnGhostShadow(Vector3 pos, Sprite sprite, bool flipX, float t)
    {
        if (sprite == null) return;
        GameObject go = new GameObject("GhostShadow");
        go.transform.position = pos;
        go.transform.localScale = Vector3.one;

        SpriteRenderer sr = go.AddComponent<SpriteRenderer>();
        sr.sprite = sprite;
        sr.flipX = flipX;
        sr.sortingOrder = 7;
        // 青碧与纯白流光混合
        Color shadowColor = Color.Lerp(new Color(0.1f, 0.8f, 1f, 0.75f), new Color(0.7f, 1f, 1f, 0.9f), t);
        sr.color = shadowColor;

        StartCoroutine(FadeShadowRoutine(go, sr, shadowColor));
    }

    private IEnumerator FadeShadowRoutine(GameObject go, SpriteRenderer sr, Color initCol)
    {
        float dur = 0.35f;
        float el = 0f;
        while (el < dur)
        {
            el += Time.deltaTime;
            float a = Mathf.Lerp(initCol.a, 0f, el / dur);
            sr.color = new Color(initCol.r, initCol.g, initCol.b, a);
            go.transform.localScale = Vector3.one * (1f + 0.15f * (el / dur));
            yield return null;
        }
        Destroy(go);
    }

    /// <summary>
    /// 生成单次断空墨爆 (冲击波环 + 十字星芒 + 星尘飞溅)
    /// </summary>
    private void SpawnDetonationBurst(Vector3 pos, int stage)
    {
        // 1. 十字极光星芒
        GameObject star = new GameObject($"Starburst_{stage}");
        star.transform.position = pos;
        SpriteRenderer starSr = star.AddComponent<SpriteRenderer>();
        starSr.sprite = starburstSprite;
        starSr.color = new Color(1f, 1f, 1f, 1f);
        starSr.sortingOrder = 22;
        star.transform.localScale = Vector3.one * (1.2f + stage * 0.4f);
        StartCoroutine(FadeAndScale(star, starSr, 0.22f, 1.8f));

        // 2. 环形水墨冲击波
        GameObject ring = new GameObject($"Shockwave_{stage}");
        ring.transform.position = pos;
        SpriteRenderer ringSr = ring.AddComponent<SpriteRenderer>();
        ringSr.sprite = shockwaveSprite;
        ringSr.color = new Color(0.1f, 0.9f, 1f, 0.95f);
        ringSr.sortingOrder = 21;
        ring.transform.localScale = Vector3.one * 0.4f;
        StartCoroutine(ExpandAndFade(ring, ringSr, 0.28f, 2.8f + stage * 0.5f));

        // 3. 飞溅的青冰星尘
        int dotCount = 10 + stage * 4;
        for (int i = 0; i < dotCount; i++)
        {
            SpawnStardustParticle(pos);
        }
    }

    private void SpawnStardustParticle(Vector3 origin)
    {
        GameObject dot = new GameObject("Stardust");
        dot.transform.position = origin;
        SpriteRenderer sr = dot.AddComponent<SpriteRenderer>();
        sr.sprite = particleDotSprite;
        sr.color = new Color(0.4f, 1f, 1f, 0.95f);
        sr.sortingOrder = 23;
        dot.transform.localScale = Vector3.one * Random.Range(0.4f, 0.9f);

        Vector2 vel = Random.insideUnitCircle.normalized * Random.Range(2.5f, 6.0f);
        StartCoroutine(ParticleRoutine(dot, sr, vel));
    }

    private IEnumerator ParticleRoutine(GameObject go, SpriteRenderer sr, Vector2 vel)
    {
        float life = Random.Range(0.25f, 0.45f);
        float el = 0f;
        Vector3 pos = go.transform.position;
        while (el < life)
        {
            el += Time.deltaTime;
            pos.x += vel.x * Time.deltaTime;
            pos.y += vel.y * Time.deltaTime;
            vel.y -= 9.8f * Time.deltaTime; // 重力下落
            go.transform.position = pos;
            sr.color = new Color(sr.color.r, sr.color.g, sr.color.b, 1f - (el / life));
            yield return null;
        }
        Destroy(go);
    }

    private IEnumerator AnimateCone(GameObject go, SpriteRenderer sr, float dir)
    {
        float dur = 0.22f;
        float el = 0f;
        Vector3 baseScale = new Vector3(dir * 1.6f, 1.4f, 1f);
        while (el < dur)
        {
            el += Time.deltaTime;
            float t = el / dur;
            go.transform.localScale = Vector3.Lerp(baseScale, new Vector3(dir * 2.2f, 0.1f, 1f), t);
            sr.color = new Color(1f, 1f, 1f, 1f - t);
            yield return null;
        }
        Destroy(go);
    }

    private IEnumerator FadeAndScale(GameObject go, SpriteRenderer sr, float duration, float scaleMult)
    {
        float el = 0f;
        Vector3 startScale = go.transform.localScale;
        Color c = sr.color;
        while (el < duration)
        {
            el += Time.deltaTime;
            float t = el / duration;
            go.transform.localScale = Vector3.Lerp(startScale, startScale * scaleMult, t);
            sr.color = new Color(c.r, c.g, c.b, Mathf.Lerp(c.a, 0f, t));
            yield return null;
        }
        Destroy(go);
    }

    private IEnumerator ExpandAndFade(GameObject go, SpriteRenderer sr, float duration, float targetScale)
    {
        float el = 0f;
        Vector3 startScale = go.transform.localScale;
        Vector3 endScale = Vector3.one * targetScale;
        Color c = sr.color;
        while (el < duration)
        {
            el += Time.deltaTime;
            float t = el / duration;
            go.transform.localScale = Vector3.Lerp(startScale, endScale, t);
            sr.color = new Color(c.r, c.g, c.b, Mathf.Lerp(c.a, 0f, t));
            yield return null;
        }
        Destroy(go);
    }

    private IEnumerator FadeAndDestroy(GameObject go, float duration)
    {
        SpriteRenderer sr = go.GetComponent<SpriteRenderer>();
        if (sr != null)
        {
            float el = 0f;
            Color c = sr.color;
            while (el < duration)
            {
                el += Time.deltaTime;
                sr.color = new Color(c.r, c.g, c.b, Mathf.Lerp(c.a, 0f, el / duration));
                yield return null;
            }
        }
        else
        {
            yield return new WaitForSeconds(duration);
        }
        Destroy(go);
    }

    /// <summary>
    /// 触发相机强震动 (Camera Trauma Shake)
    /// </summary>
    public void TriggerCameraShake(float intensity, float duration)
    {
        Camera cam = Camera.main;
        if (cam != null)
        {
            StartCoroutine(CameraShakeRoutine(cam, intensity, duration));
        }
    }

    private IEnumerator CameraShakeRoutine(Camera cam, float intensity, float duration)
    {
        Vector3 originalPos = cam.transform.position;
        float el = 0f;
        while (el < duration)
        {
            el += Time.unscaledDeltaTime;
            float damp = 1f - (el / duration);
            float ox = (Random.value * 2f - 1f) * intensity * damp;
            float oy = (Random.value * 2f - 1f) * intensity * damp;
            cam.transform.position = originalPos + new Vector3(ox, oy, 0f);
            yield return null;
        }
        cam.transform.position = originalPos;
    }

    // =========================================================================
    // 程序化纹理生成算法 (Procedural Texture & Sprite Builders)
    // =========================================================================

    private Sprite CreateCrossStarburst(int w, int h)
    {
        Texture2D tex = new Texture2D(w, h, TextureFormat.RGBA32, false);
        tex.filterMode = FilterMode.Bilinear;
        Color[] cols = new Color[w * h];
        float cx = w * 0.5f;
        float cy = h * 0.5f;

        for (int y = 0; y < h; y++)
        {
            for (int x = 0; x < w; x++)
            {
                float dx = Mathf.Abs(x - cx);
                float dy = Mathf.Abs(y - cy);
                float dist = Mathf.Sqrt(dx * dx + dy * dy);

                // 十字主光芒 (横向贯通 + 纵向窄芒)
                float horizBeam = Mathf.Exp(-dy * 0.12f) * Mathf.Max(0, 1f - dx / (w * 0.5f));
                float vertBeam = Mathf.Exp(-dx * 0.15f) * Mathf.Max(0, 1f - dy / (h * 0.5f));
                float core = Mathf.Max(0, 1f - dist / (w * 0.25f));

                float val = Mathf.Clamp01(horizBeam * 1.4f + vertBeam * 1.1f + core * 1.5f);
                Color c = Color.Lerp(new Color(0.2f, 0.9f, 1f, 0f), Color.white, val * val);
                c.a = Mathf.Clamp01(val);
                cols[y * w + x] = c;
            }
        }
        tex.SetPixels(cols);
        tex.Apply();
        return Sprite.Create(tex, new Rect(0, 0, w, h), new Vector2(0.5f, 0.5f), 100f);
    }

    private Sprite CreateShockwaveRing(int w, int h)
    {
        Texture2D tex = new Texture2D(w, h, TextureFormat.RGBA32, false);
        tex.filterMode = FilterMode.Bilinear;
        Color[] cols = new Color[w * h];
        float cx = w * 0.5f;
        float cy = h * 0.5f;
        float targetR = w * 0.42f;
        float thickness = w * 0.08f;

        for (int y = 0; y < h; y++)
        {
            for (int x = 0; x < w; x++)
            {
                float dist = Vector2.Distance(new Vector2(x, y), new Vector2(cx, cy));
                float diff = Mathf.Abs(dist - targetR);
                float val = Mathf.Max(0, 1f - (diff / thickness));
                val = Mathf.Pow(val, 1.8f);

                Color c = Color.Lerp(new Color(0.1f, 0.7f, 1f, 0f), Color.white, val);
                c.a = val;
                cols[y * w + x] = c;
            }
        }
        tex.SetPixels(cols);
        tex.Apply();
        return Sprite.Create(tex, new Rect(0, 0, w, h), new Vector2(0.5f, 0.5f), 100f);
    }

    private Sprite CreateVoidCone(int w, int h)
    {
        Texture2D tex = new Texture2D(w, h, TextureFormat.RGBA32, false);
        tex.filterMode = FilterMode.Bilinear;
        Color[] cols = new Color[w * h];

        for (int y = 0; y < h; y++)
        {
            float normY = ((float)y / h) - 0.5f; // -0.5 ~ +0.5
            for (int x = 0; x < w; x++)
            {
                float normX = (float)x / w; // 0 (根部) ~ 1 (尖端)
                // 锥形展开角：从根部向前变宽，再在前端收缩为锐利剑尖
                float halfWidth = Mathf.Sin(normX * Mathf.PI) * 0.45f;
                float distFromCenter = Mathf.Abs(normY);

                if (distFromCenter < halfWidth)
                {
                    float innerRatio = 1f - (distFromCenter / Mathf.Max(0.001f, halfWidth));
                    float core = Mathf.Pow(innerRatio, 2.5f);
                    Color c = Color.Lerp(new Color(0.1f, 0.85f, 1f, 0.8f), Color.white, core);
                    c.a = Mathf.Clamp01(innerRatio * Mathf.Sin(normX * Mathf.PI));
                    cols[y * w + x] = c;
                }
                else
                {
                    cols[y * w + x] = Color.clear;
                }
            }
        }
        tex.SetPixels(cols);
        tex.Apply();
        return Sprite.Create(tex, new Rect(0, 0, w, h), new Vector2(0.0f, 0.5f), 100f);
    }

    private Sprite CreateFlyingSword(int w, int h)
    {
        Texture2D tex = new Texture2D(w, h, TextureFormat.RGBA32, false);
        tex.filterMode = FilterMode.Bilinear;
        Color[] cols = new Color[w * h];

        for (int y = 0; y < h; y++)
        {
            float ny = Mathf.Abs(((float)y / h) - 0.5f) * 2f; // 0 (脊) ~ 1 (刃)
            for (int x = 0; x < w; x++)
            {
                float nx = (float)x / w; // 0 (柄) ~ 1 (尖)
                float bladeWidth = nx < 0.85f ? 0.35f : (1f - nx) / 0.15f * 0.35f;

                if (ny < bladeWidth)
                {
                    float spine = 1f - (ny / Mathf.Max(0.001f, bladeWidth));
                    Color c = Color.Lerp(new Color(0.15f, 0.9f, 1f, 0.85f), Color.white, spine * spine);
                    cols[y * w + x] = c;
                }
                else
                {
                    cols[y * w + x] = Color.clear;
                }
            }
        }
        tex.SetPixels(cols);
        tex.Apply();
        return Sprite.Create(tex, new Rect(0, 0, w, h), new Vector2(0.5f, 0.5f), 100f);
    }

    private Sprite CreateSpatialRift(int w, int h)
    {
        Texture2D tex = new Texture2D(w, h, TextureFormat.RGBA32, false);
        tex.filterMode = FilterMode.Bilinear;
        Color[] cols = new Color[w * h];

        for (int y = 0; y < h; y++)
        {
            for (int x = 0; x < w; x++)
            {
                float nx = (float)x / w;
                float wave = Mathf.Sin(nx * 28f) * 0.22f + Mathf.Cos(nx * 14f) * 0.12f;
                float ny = ((float)y / h) - 0.5f;
                float dist = Mathf.Abs(ny - wave);

                if (dist < 0.25f)
                {
                    float factor = 1f - (dist / 0.25f);
                    // 内部墨黑，边缘发亮青色电弧
                    Color edge = new Color(0.2f, 0.95f, 1f, factor);
                    Color ink = new Color(0.02f, 0.05f, 0.08f, factor);
                    cols[y * w + x] = factor > 0.6f ? ink : edge;
                }
                else
                {
                    cols[y * w + x] = Color.clear;
                }
            }
        }
        tex.SetPixels(cols);
        tex.Apply();
        return Sprite.Create(tex, new Rect(0, 0, w, h), new Vector2(0.5f, 0.5f), 100f);
    }

    private Sprite CreateFrostDecal(int w, int h)
    {
        Texture2D tex = new Texture2D(w, h, TextureFormat.RGBA32, false);
        tex.filterMode = FilterMode.Bilinear;
        Color[] cols = new Color[w * h];

        for (int y = 0; y < h; y++)
        {
            float ny = (float)y / h;
            for (int x = 0; x < w; x++)
            {
                float nx = (float)x / w;
                float edge = Mathf.Sin(nx * Mathf.PI);
                float crack = Mathf.PerlinNoise(nx * 15f, ny * 10f);

                if (crack > 0.35f && ny < 0.8f)
                {
                    float alpha = edge * (crack - 0.35f) * 1.5f;
                    cols[y * w + x] = new Color(0.7f, 0.95f, 1f, Mathf.Clamp01(alpha));
                }
                else
                {
                    cols[y * w + x] = Color.clear;
                }
            }
        }
        tex.SetPixels(cols);
        tex.Apply();
        return Sprite.Create(tex, new Rect(0, 0, w, h), new Vector2(0.5f, 0.1f), 100f);
    }

    private Sprite CreateParticleDot(int w, int h)
    {
        Texture2D tex = new Texture2D(w, h, TextureFormat.RGBA32, false);
        tex.filterMode = FilterMode.Bilinear;
        Color[] cols = new Color[w * h];
        float cx = w * 0.5f;
        float cy = h * 0.5f;

        for (int y = 0; y < h; y++)
        {
            for (int x = 0; x < w; x++)
            {
                float d = Vector2.Distance(new Vector2(x, y), new Vector2(cx, cy)) / (w * 0.5f);
                float a = Mathf.Max(0, 1f - d);
                cols[y * w + x] = new Color(1f, 1f, 1f, a * a);
            }
        }
        tex.SetPixels(cols);
        tex.Apply();
        return Sprite.Create(tex, new Rect(0, 0, w, h), new Vector2(0.5f, 0.5f), 100f);
    }
}
