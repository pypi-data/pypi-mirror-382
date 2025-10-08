import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { IMainMenu } from '@jupyterlab/mainmenu';

import { showDialog, Dialog } from '@jupyterlab/apputils';

/**
 * Initialization data for the jupyterlab_close_all_tabs_extension extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyterlab_close_all_tabs_extension:plugin',
  description:
    "Small extension to add menu item under 'Tabs' to allow close all open tabs",
  autoStart: true,
  requires: [IMainMenu],
  activate: (app: JupyterFrontEnd, mainMenu: IMainMenu) => {
    console.log(
      'JupyterLab extension jupyterlab_close_all_tabs_extension is activated!'
    );

    const { commands, shell } = app;

    // Add command to close all tabs
    const commandID = 'tabs:close-all';
    commands.addCommand(commandID, {
      label: 'Close All Tabs',
      caption: 'Close all open tabs',
      execute: async () => {
        // Show confirmation dialog
        const result = await showDialog({
          title: 'Close All Tabs',
          body: 'Are you sure you want to close all open tabs?',
          buttons: [
            Dialog.cancelButton({ label: 'Cancel' }),
            Dialog.okButton({ label: 'Close All' })
          ]
        });

        if (result.button.accept) {
          // Get all widgets in the main area
          const widgets = Array.from(shell.widgets('main'));

          // Close all widgets
          for (const widget of widgets) {
            widget.close();
          }
        }
      }
    });

    // Add command to Tabs menu
    mainMenu.tabsMenu.addGroup([{ command: commandID }], 100);
  }
};

export default plugin;
