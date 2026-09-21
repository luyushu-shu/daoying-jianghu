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

    Animator animator;
    SpriteRenderer spriteRenderer;
    CombatActor combat;

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
}
