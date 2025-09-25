using System;
using System.Diagnostics;
using System.Net.Http;
using System.Security.Principal;
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using m1pplauncher.Services;

namespace m1pplauncher.ViewModels;

public partial class MainViewModel : ObservableObject
{
  [ObservableProperty]
  [NotifyPropertyChangedFor(nameof(IsConnectButtonVisible))]
  [NotifyPropertyChangedFor(nameof(IsDisconnectButtonVisible))]
  public partial bool IsLazerInstalled { get; set; }

  [ObservableProperty]
  public partial bool IsAvailable { get; set; }

  [ObservableProperty]
  public partial bool IsFetchingAvailability { get; set; }

  [ObservableProperty]
  public partial bool IsPpyShBlocked { get; set; }

  [ObservableProperty]
  [NotifyPropertyChangedFor(nameof(IsBlockPpyShCheckBoxEnabled))]
  public partial bool IsBlockingPpySh { get; set; }

  [ObservableProperty]
  [NotifyPropertyChangedFor(nameof(IsBlockPpyShCheckBoxEnabled))]
  public partial bool CanBlockPpySh { get; set; }

  [ObservableProperty]
  [NotifyPropertyChangedFor(nameof(IsConnectButtonVisible))]
  [NotifyPropertyChangedFor(nameof(IsDisconnectButtonVisible))]
  public partial bool IsConnected { get; set; }

  [ObservableProperty]
  [NotifyPropertyChangedFor(nameof(IsConnectButtonVisible))]
  [NotifyPropertyChangedFor(nameof(IsDisconnectButtonVisible))]
  public partial bool IsConnecting { get; set; }

  [ObservableProperty]
  [NotifyPropertyChangedFor(nameof(DownloadPercentage))]
  public partial double ConnectDownloadProgress { get; set; }

  [ObservableProperty]
  [NotifyPropertyChangedFor(nameof(IsConnectButtonVisible))]
  [NotifyPropertyChangedFor(nameof(IsDisconnectButtonVisible))]
  public partial bool IsLazerRunning { get; set; }

  [ObservableProperty]
  [NotifyPropertyChangedFor(nameof(IsUpdateAvailable))]
  [NotifyPropertyChangedFor(nameof(LatestReleaseUrl))]
  public partial string? LatestVersion { get; set; }

  [ObservableProperty]
  public partial bool IsCheckingForUpdate { get; set; }

  public bool IsUpdateAvailable => LatestVersion is not null;

  public string LatestReleaseUrl => $"https://github.com/{UpdateCheckerService.REPO}/releases/tag/{LatestVersion}";

  public string DownloadPercentage => $"{ConnectDownloadProgress:0.##}%";

  public bool IsBlockPpyShCheckBoxEnabled => !IsBlockingPpySh && CanBlockPpySh;

  public bool IsConnectButtonVisible => !IsConnected && IsLazerInstalled && !IsConnecting && !IsLazerRunning;

  public bool IsDisconnectButtonVisible => IsConnected && IsLazerInstalled && !IsConnecting && !IsLazerRunning;

  public async Task InitializeAsync()
  {
    IsLazerInstalled = await LazerService.InitializeAsync();
    if (IsLazerInstalled)
    {
      LazerService.LazerRunningChanged += running => IsLazerRunning = running;
      IsConnected = LazerService.IsRulesetInstalled();
    }

    CanBlockPpySh = new WindowsPrincipal(WindowsIdentity.GetCurrent()).IsInRole(WindowsBuiltInRole.Administrator);

    try
    {
      IsBlockingPpySh = true;
      IsPpyShBlocked = await HostsService.IsPpyBlockedAsync();
      IsBlockingPpySh = false;
    }
    catch (Exception ex)
    {
      IsBlockingPpySh = false;
      await DialogService.ShowMessageAsync("Could not access the hosts file", ex.Message);
    }

    try
    {
      IsFetchingAvailability = true;

      using HttpClient http = new()
      {
        Timeout = TimeSpan.FromSeconds(1)
      };

      HttpResponseMessage response = await http.GetAsync("https://lazer-api.m1pposu.dev/");
      IsAvailable = response.IsSuccessStatusCode;

      IsFetchingAvailability = false;
    }
    catch (Exception ex)
    {
      IsFetchingAvailability = false;
      await DialogService.ShowMessageAsync("Could not fetch server status", ex.Message);
    }

    try
    {
      IsCheckingForUpdate = true;
      await Task.Delay(99999);
      LatestVersion = await UpdateCheckerService.IsLatestVersionAsync();
      IsCheckingForUpdate = false;
    }
    catch (Exception ex)
    {
      IsCheckingForUpdate = false;
      await DialogService.ShowMessageAsync("Could not check for updates", ex.Message);
    }
  }

  [RelayCommand]
  private async Task BlockPpyShAsync()
  {
    try
    {
      IsBlockingPpySh = true;

      if (IsPpyShBlocked)
        await HostsService.BlockPpyAsync();
      else
        await HostsService.UnblockPpyAsync();

      await Task.Delay(500);

      IsBlockingPpySh = false;
    }
    catch (Exception ex)
    {
      IsBlockingPpySh = false;
      IsPpyShBlocked = !IsPpyShBlocked;
      await DialogService.ShowMessageAsync("Could not block ppy.sh", ex.Message);
    }
  }

  [RelayCommand]
  private async Task ConnectAsync()
  {
    try
    {
      IsConnecting = true;
      ConnectDownloadProgress = 0;

      await LazerService.InstallRulesetAsync(x => ConnectDownloadProgress = x);
      await Task.Delay(500);

      IsConnected = true;
      IsConnecting = false;
    }
    catch (Exception ex)
    {
      IsConnecting = false;
      await DialogService.ShowMessageAsync("Could not connect", ex.Message);
    }
  }

  [RelayCommand]
  private async Task DisconnectAsync()
  {
    try
    {
      LazerService.RemoveRulesetAsync();
      IsConnected = false;
    }
    catch (Exception ex)
    {
      await DialogService.ShowMessageAsync("Could not disconnect", ex.Message);
    }
  }

  [RelayCommand]
  private void OpenGitHubIssues()
    => Process.Start(new ProcessStartInfo() { FileName = "https://github.com/M1PPosu/m1lazer-launcher/issues", UseShellExecute = true });

  [RelayCommand]
  private void OpenWebsite()
    => Process.Start(new ProcessStartInfo() { FileName = "https://lazer.m1pposu.dev/", UseShellExecute = true });

  [RelayCommand]
  private void PromptAdministrator()
  {
    try
    {
      Process p = Process.Start(new ProcessStartInfo()
      {
        FileName = Environment.ProcessPath!,
        Verb = "runas",
        UseShellExecute = true
      })!;

      Environment.Exit(0);
    }
    catch { }
  }

  [RelayCommand]
  private void LaunchLazer()
  {
    Process.Start(LazerService.LAZER_EXECUTABLE_PATH);
  }
}
