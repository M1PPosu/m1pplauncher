using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Threading.Tasks;
using System.Timers;
using Microsoft.UI.Xaml;
using Windows.System;

namespace m1pplauncher.Services;

internal static class LazerService
{
  private const string RULESET_DOWNLOAD_URL = "https://github.com/m1pposu/LazerAuthlibInjection/releases/latest/download/ruleset.dll";
  private const string CONFIG_DOWNLOAD_URL = "https://github.com/m1pposu/LazerAuthlibInjection/releases/latest/download/config.json";
  private static readonly string LAZER_STORAGE_INI_PATH = Path.Combine(Environment.GetEnvironmentVariable("appdata")!, "osu", "storage.ini");
  private static string _rulesetPath = null!;
  private static string _configPath = null!;
  private static readonly DispatcherTimer _lazerTrackerTimer = new() { Interval = TimeSpan.FromSeconds(0.2) };

  public static readonly string LAZER_EXECUTABLE_PATH = Path.Combine(Environment.GetEnvironmentVariable("localappdata")!, "osulazer", "current", "osu!.exe");
  public static event Action<bool>? LazerRunningChanged = null;

  public static async Task<bool> InitializeAsync()
  {
    if (!File.Exists(LAZER_STORAGE_INI_PATH))
      return false;

    string[] lines = await File.ReadAllLinesAsync(LAZER_STORAGE_INI_PATH);
    if (lines.FirstOrDefault(x => x.StartsWith("FullPath = ")) is not string fullPath)
      return false;

    string userStoragePath = fullPath[11..];
    _rulesetPath = Path.Combine(userStoragePath, "rulesets", "m1pplazer.dll");
    _configPath = Path.Combine(userStoragePath, "authlib_local_config.json");

    _lazerTrackerTimer.Tick += (_, _) =>
    {
      bool isLazerRunning = Process.GetProcesses().Any(x => x.ProcessName == "osu!");
      LazerRunningChanged?.Invoke(isLazerRunning);
    };
    _lazerTrackerTimer.Start();

    return true;
  }

  public static bool IsRulesetInstalled() => File.Exists(_rulesetPath);

  public static async Task InstallRulesetAsync(Action<double> progressCallback)
  {
    using HttpClient http = new();
    HttpResponseMessage response = await http.GetAsync(RULESET_DOWNLOAD_URL, HttpCompletionOption.ResponseHeadersRead);
    response.EnsureSuccessStatusCode();

    using MemoryStream ruleset = new();
    var buffer = new byte[8192];
    long progress = 0;
    int read;
    while ((read = await (await response.Content.ReadAsStreamAsync()).ReadAsync(buffer)) > 0)
    {
      progress += read;
      await ruleset.WriteAsync(buffer.AsMemory(0, read));
      progressCallback?.Invoke(progress * 1d / (response.Content.Headers.ContentLength!.Value) * 100);
    }

    byte[] config = await http.GetByteArrayAsync(CONFIG_DOWNLOAD_URL);
    await File.WriteAllBytesAsync(_rulesetPath, ruleset.ToArray());
    await File.WriteAllBytesAsync(_configPath, config);
  }

  public static void RemoveRulesetAsync()
  {
    File.Delete(_rulesetPath);
    File.Delete(_configPath);
  }
}
