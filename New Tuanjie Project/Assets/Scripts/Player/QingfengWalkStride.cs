/// <summary>
/// 青锋行走 15 帧的步幅元数据（PPU=100，每帧 140ms，周期 2.1s）。
/// 接触帧前后靴距约 42.8px；两步一个循环。
/// 设计移速 = 每周期步数 × 步幅像素 / 周期秒 / PPU。
/// </summary>
public static class QingfengWalkStride
{
    public const float Fps = 1000f / 140f;
    public const float PixelsPerUnit = 100f;
    public const int FrameCount = 15;
    public const int StepsPerCycle = 2;
    public const float CycleSeconds = 2.1f;
    public const float StepDistancePixels = 42.8f;

    /// <summary>零打滑设计移速（世界单位/秒）。约 0.407。</summary>
    public const float DesignMoveSpeed =
        StepsPerCycle * StepDistancePixels / CycleSeconds / PixelsPerUnit;
}
