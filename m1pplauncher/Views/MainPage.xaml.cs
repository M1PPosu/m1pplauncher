using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;

namespace m1pplauncher.Views;

public sealed partial class MainPage : Page
{
  public UIElement AppTitleBar => TitleBar;

  public MainPage()
  {
    InitializeComponent();

    _ = ViewModel.InitializeAsync();
  }
}
