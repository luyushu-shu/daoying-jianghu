/// <summary>
/// 青锋奔跑 8 帧步幅（PPU=100，约 18.5 FPS，周期 0.43s）。
/// 半周期 4 帧：R1 接触 + R2 蹬离 + R3 腾空 + R4 将落。
/// 接触帧前后靴距约 72.8px。R1 内侧近靴在前，R5 外侧远靴在前。
/// </summary>
public static class QingfengRunStride
{
    public const float Fps = 18.52f;
    public const float PixelsPerUnit = 100f;
    public const int FramesPerStep = 4;
    public const float StepDistancePixels = 72.8f;
    public const float RunAnimThreshold = 0.55f;

    /// <summary>零打滑设计移速（世界单位/秒）。约 3.37。</summary>
    public const float DesignMoveSpeed =
        StepDistancePixels * (Fps / FramesPerStep) / PixelsPerUnit;
}
