using System.Collections;
using UnityEngine;

/// <summary>
/// 杂兵刀手预览行为：同台测试青锋与刀兵所有动作，支持自动巡逻/横斩与按键测试。
/// 快捷键：Tab切换控制角色，数字键1触发刀兵横斩，2触发刀兵行走，3触发刀兵待机。
/// </summary>
public class MookPreviewActor : MonoBehaviour
{
    public const string MookName = "MookSwordsman";

    public Animator animator;
    public SpriteRenderer spriteRenderer;

    public Transform playerTr;
    public float patrolSpeed = 1.8f;
    public float attackRange = 1.6f;
    public float detectRange = 6.0f;

    float attackCooldown = 0f;
    bool isAttacking = false;
    float attackTimer = 0f;
    const float AttackDuration = 0.85f;
    bool hitFlashedThisAttack = false;

    public static void SpawnIfMissing()
    {
        if (GameObject.Find(MookName) != null) return;

        GameObject qingfeng = GameObject.Find("QingfengIdle");
        float groundY = qingfeng != null ? qingfeng.transform.position.y : 0f;

        GameObject mookGo = new GameObject(MookName);
        mookGo.transform.position = new Vector3(2.5f, groundY, 0f);

        SpriteRenderer sr = mookGo.AddComponent<SpriteRenderer>();
        sr.sortingOrder = 7;
#if UNITY_EDITOR
        sr.sprite = UnityEditor.AssetDatabase.LoadAssetAtPath<Sprite>("Assets/Sprites/Enemies/MookSwordsman/Idle/idle-1.png");
#endif
        Animator anim = mookGo.AddComponent<Animator>();
        RuntimeAnimatorController ctrl = EnemyVisualLoader.LoadSwordsmanController();
        if (ctrl == null) ctrl = PlayerVisualLoader.LoadController();
        anim.runtimeAnimatorController = ctrl;
        anim.SetInteger("Character", 1);
        anim.SetBool("IsGrounded", true);

        MookPreviewActor actor = mookGo.AddComponent<MookPreviewActor>();
        actor.animator = anim;
        actor.spriteRenderer = sr;
        if (qingfeng != null) actor.playerTr = qingfeng.transform;
    }

    void Awake()
    {
        if (animator == null) animator = GetComponent<Animator>();
        if (spriteRenderer == null) spriteRenderer = GetComponent<SpriteRenderer>();
        if (animator != null)
        {
            if (animator.runtimeAnimatorController == null)
            {
                RuntimeAnimatorController ctrl = EnemyVisualLoader.LoadSwordsmanController();
                if (ctrl == null) ctrl = PlayerVisualLoader.LoadController();
                animator.runtimeAnimatorController = ctrl;
            }
            if (animator.runtimeAnimatorController != null)
            {
                animator.SetInteger("Character", 1);
                animator.SetBool("IsGrounded", true);
            }
        }
    }

    void Update()
    {
        if (animator == null || animator.runtimeAnimatorController == null) return;

        if (attackCooldown > 0f) attackCooldown -= Time.deltaTime;

        if (isAttacking)
        {
            attackTimer -= Time.deltaTime;
            if (attackTimer <= 0f)
            {
                isAttacking = false;
            }
            return;
        }

        // 自动电脑 AI 行为
        if (playerTr == null)
        {
            GameObject qf = GameObject.Find("QingfengIdle");
            if (qf != null) playerTr = qf.transform;
            if (playerTr == null) return;
        }

        float dx = playerTr.position.x - transform.position.x;
        float dist = Mathf.Abs(dx);

        // 朝向玩家
        if (spriteRenderer != null)
            spriteRenderer.flipX = dx < 0;

        if (dist <= attackRange)
        {
            // 进入近身攻击范围：停止行进并拔刀横斩
            animator.SetFloat("Speed", 0f);
            if (attackCooldown <= 0f)
            {
                TriggerAttack();
            }
        }
        else if (dist <= detectRange)
        {
            // 发现玩家：以 15 帧平缓步伐逼近
            float dir = Mathf.Sign(dx);
            animator.SetFloat("Speed", 0.4f);
            Vector3 p = transform.position;
            p.x += dir * patrolSpeed * Time.deltaTime;
            transform.position = p;
        }
        else
        {
            animator.SetFloat("Speed", 0f);
        }
    }

    public void TriggerAttack()
    {
        if (animator == null) return;
        isAttacking = true;
        attackTimer = AttackDuration;
        attackCooldown = 1.6f;
        animator.SetFloat("Speed", 0f);
        animator.SetTrigger("AttackA");
    }

    public void FlashHit()
    {
        StartCoroutine(FlashRoutine());
    }

    IEnumerator FlashRoutine()
    {
        if (spriteRenderer == null) yield break;
        spriteRenderer.color = new Color(1f, 0.4f, 0.4f);
        yield return new WaitForSeconds(0.12f);
        if (spriteRenderer != null) spriteRenderer.color = Color.white;
    }
}
