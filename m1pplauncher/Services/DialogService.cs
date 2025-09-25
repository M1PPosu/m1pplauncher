using System;
using System.Threading.Tasks;
using Microsoft.UI.Xaml.Controls;

namespace m1pplauncher.Services;

public static class DialogService
{
  public static async Task ShowMessageAsync(string title, string message)
  {
    ContentDialog dialog = new()
    {
      Title = title,
      Content = message,
      CloseButtonText = "OK",
      XamlRoot = App.MainWindow.Content.XamlRoot
    };

    await dialog.ShowAsync();
  }
}
