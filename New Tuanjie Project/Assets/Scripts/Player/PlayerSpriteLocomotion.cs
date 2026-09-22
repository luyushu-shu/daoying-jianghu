using UnityEngine;

/// <summary>
/// 预览场景：A/D 行走，Shift+A/D 奔跑。战斗场景由 CombatActor 写 Speed。
/// </summary>
[RequireComponent(typeof(Animator))]
[RequireComponent(typeof(SpriteRenderer))]
public class PlayerSpriteLocomotion : MonoBehaviour
{
    const float WalkThreshold = 0.1f;
    const float WalkAnimSpeed = 0.4f;
    const float DodgeDuration = 0.60f;
    const float DodgeDistance = 0.45f;
    const float DodgeMoveDuration = 0.20f;

    Animator animator;
    SpriteRenderer spriteRenderer;
    CombatActor combat;
    float dodgeTimer = 0f;
    float dodgeDir = 1f;

    int attackStep = 0;
    float attackTimer = 0f;
    float comboWindow = 0f;
    float lungeTimer = 0f;
    float lungeSpeed = 0f;

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
    }

    void Update()
    {
        if (combat != null) return;

        // 闪避状态位移（略微前移一小段，前半段冲刺位移，后半段着地收招）
        if (dodgeTimer > 0f)
        {
            float prevTimer = dodgeTimer;
            dodgeTimer -= Time.deltaTime;
            if (dodgeTimer < 0f) dodgeTimer = 0f;

            float elapsed = DodgeDuration - prevTimer;
            if (elapsed < DodgeMoveDuration)
            {
                float moveDt = Mathf.Min(Time.deltaTime, DodgeMoveDuration - elapsed);
                float speed = DodgeDistance / DodgeMoveDuration;
                Vector3 dp = transform.position;
                dp.x += dodgeDir * speed * moveDt;
                transform.position = dp;
            }
            return;
        }

        // 攻击连段窗口更新
        if (comboWindow > 0f)
        {
            comboWindow -= Time.deltaTime;
            if (comboWindow <= 0f) attackStep = 0;
        }

        // 攻击硬直与出剑前踏微位移
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

            // 攻击期间允许空格打断/取消进闪避
            if (Input.GetKeyDown(KeyCode.Space))
            {
                attackTimer = 0f;
                attackStep = 0;
                comboWindow = 0f;
                lungeTimer = 0f;
                StartDodge();
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
            return;
        }

        // 触发闪避 (Space)
        if (Input.GetKeyDown(KeyCode.Space))
        {
            StartDodge();
            return;
        }

        // 触发轻攻击三连斩 (J 或 鼠标左键)
        if (Input.GetKeyDown(KeyCode.J) || Input.GetMouseButtonDown(0))
        {
            PerformNextAttack();
            return;
        }

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
            }
            else
            {
                animSpeed = WalkAnimSpeed;
                moveSpeed = QingfengWalkStride.DesignMoveSpeed;
            }
        }

        animator.SetFloat("Speed", animSpeed);

        if (Mathf.Abs(mx) > WalkThreshold)
        {
            spriteRenderer.flipX = mx < 0f;
            Vector3 p = transform.position;
            p.x += mx * moveSpeed * Time.deltaTime;
            transform.position = p;
        }
    }

    void StartDodge()
    {
        dodgeDir = spriteRenderer.flipX ? -1f : 1f;
        if (Input.GetKey(KeyCode.A) || Input.GetKey(KeyCode.LeftArrow)) dodgeDir = -1f;
        if (Input.GetKey(KeyCode.D) || Input.GetKey(KeyCode.RightArrow)) dodgeDir = 1f;
        spriteRenderer.flipX = dodgeDir < 0f;

        dodgeTimer = DodgeDuration;
        animator.SetTrigger("Dodge");
    }

    void PerformNextAttack()
    {
        if (attackStep == 0 || comboWindow <= 0f)
        {
            attackStep = 1;
            attackTimer = 0.34f;
            comboWindow = 0.55f;
            lungeTimer = 0.10f;
            lungeSpeed = 0.15f / 0.10f;
            animator.SetTrigger("Attack1");
        }
        else if (attackStep == 1)
        {
            attackStep = 2;
            attackTimer = 0.34f;
            comboWindow = 0.55f;
            lungeTimer = 0.10f;
            lungeSpeed = 0.20f / 0.10f;
            animator.SetTrigger("Attack2");
        }
        else if (attackStep == 2)
        {
            attackStep = 3;
            attackTimer = 0.38f;
            comboWindow = 0f;
            lungeTimer = 0.12f;
            lungeSpeed = 0.25f / 0.12f;
            animator.SetTrigger("Attack3");
        }
    }
}
