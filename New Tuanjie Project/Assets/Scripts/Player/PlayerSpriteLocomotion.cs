using UnityEngine;

/// <summary>
/// 预览场景：A/D 驱动 Speed，切换待机/行走，并让角色真正横移。
/// 战斗场景由 CombatActor 写 Speed，本组件只在没有 CombatActor 时自己读输入。
/// </summary>
[RequireComponent(typeof(Animator))]
[RequireComponent(typeof(SpriteRenderer))]
public class PlayerSpriteLocomotion : MonoBehaviour
{
    const float WalkThreshold = 0.1f;

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

        animator.SetFloat("Speed", Mathf.Abs(mx));

        if (Mathf.Abs(mx) > WalkThreshold)
        {
            spriteRenderer.flipX = mx < 0f;
            Vector3 p = transform.position;
            p.x += mx * QingfengWalkStride.DesignMoveSpeed * Time.deltaTime;
            transform.position = p;
        }
    }
}
