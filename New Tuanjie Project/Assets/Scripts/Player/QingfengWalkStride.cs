/// <summary>
/// 青锋行走 8 帧的步幅元数据（PPU=100，12 FPS）。
/// 短步轻走：接触帧前后靴距约 51px，支撑脚画布位移有限。
/// 设计移速 = 步幅像素 × (FPS / 每步帧数) / PPU。
/// </summary>
public static class QingfengWalkStride
{
    public const float Fps = 12f;
    public const float PixelsPerUnit = 100f;
    public const int FramesPerStep = 4;
    public const float StepDistancePixels = 51f;

    /// <summary>零打滑设计移速（世界单位/秒）。约 1.53。</summary>
    public const float DesignMoveSpeed =
        StepDistancePixels * (Fps / FramesPerStep) / PixelsPerUnit;
}
