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
    const float JumpVelocity = 8.5f;
    const float Gravity = 24.0f;
    const float BlockDuration = 0.68f;
    const float ParryWindow = 0.18f;

    Animator animator;
    SpriteRenderer spriteRenderer;
    CombatActor combat;
    float dodgeTimer = 0f;
    float dodgeDir = 1f;
    float blockTimer = 0f;

    public bool IsBlocking => blockTimer > 0f;
    public bool IsParryWindow => blockTimer > 0f && (BlockDuration - blockTimer) <= ParryWindow;

    float velY = 0f;
    float groundY = 0f;
    bool isGrounded = true;

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
        groundY = transform.position.y;
    }

    void Update()
    {
        if (combat != null) return;

        // 空中运动与重力解算
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
                animator.SetBool("IsGrounded", true);
            }
            transform.position = p;
        }

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

        // 格挡状态维持与取消处理
        if (blockTimer > 0f)
        {
            blockTimer -= Time.deltaTime;
            if (blockTimer < 0f) blockTimer = 0f;

            // 格挡期间允许按空格紧急闪避打断
            if (Input.GetKeyDown(KeyCode.Space))
            {
                blockTimer = 0f;
                StartDodge();
                return;
            }

            // 格挡期间允许反击（轻击/重刺）
            if (Input.GetKeyDown(KeyCode.J) || Input.GetMouseButtonDown(0))
            {
                blockTimer = 0f;
                PerformNextAttack();
                return;
            }

            if (Input.GetKeyDown(KeyCode.K) || Input.GetMouseButtonDown(1))
            {
                blockTimer = 0f;
                PerformHeavyThrust();
                return;
            }

            // 长按 F 维持格挡姿态
            if (Input.GetKey(KeyCode.F) && blockTimer < 0.25f)
            {
                blockTimer = 0.25f;
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

            // 攻击期间允许空格打断/取消进闪避（仅轻攻击允许，重刺不可打断）
            if (Input.GetKeyDown(KeyCode.Space) && attackStep < 4)
            {
                attackTimer = 0f;
                attackStep = 0;
                comboWindow = 0f;
                lungeTimer = 0f;
                StartDodge();
                return;
            }

            // 攻击期间允许按 F 取消进格挡招架（仅轻攻击允许）
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

            // 轻攻击中段接重刺终结（A_L2H）
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

        // 触发跳跃 (W / 向上键 / W+Space)
        bool jumpInput = Input.GetKeyDown(KeyCode.W) || Input.GetKeyDown(KeyCode.UpArrow) || (Input.GetKey(KeyCode.W) && Input.GetKeyDown(KeyCode.Space));
        if (jumpInput && isGrounded && dodgeTimer <= 0f)
        {
            isGrounded = false;
            velY = JumpVelocity;
            animator.SetBool("IsGrounded", false);
            animator.SetTrigger("Jump");
        }

        // 触发闪避 (Space，且未按住 W)
        if (Input.GetKeyDown(KeyCode.Space) && !Input.GetKey(KeyCode.W))
        {
            StartDodge();
            return;
        }

        // 触发格挡招架 (F 键)
        if (Input.GetKeyDown(KeyCode.F) && isGrounded && dodgeTimer <= 0f)
        {
            PerformBlock();
            return;
        }

        // 触发重刺 (K 或 鼠标右键)
        if (Input.GetKeyDown(KeyCode.K) || Input.GetMouseButtonDown(1))
        {
            PerformHeavyThrust();
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
            float airFactor = isGrounded ? 1f : 0.8f;
            p.x += mx * moveSpeed * airFactor * Time.deltaTime;
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

    void PerformHeavyThrust()
    {
        attackStep = 4;
        attackTimer = 0.76f;
        comboWindow = 0f;
        lungeTimer = 0.18f;
        lungeSpeed = 0.40f / 0.18f;
        animator.SetTrigger("HeavyThrust");
    }

    void PerformBlock()
    {
        attackStep = 0;
        attackTimer = 0f;
        comboWindow = 0f;
        lungeTimer = 0f;
        blockTimer = BlockDuration;
        animator.SetTrigger("Block");
    }
}
