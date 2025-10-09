import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { INotebookTracker } from '@jupyterlab/notebook';

/**
 * Initialization data for the jupyter-ra-extension extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyter-ra-extension:plugin',
  description: 'Relational Algebra Symbols in Jupyter Lab',
  autoStart: true,
  requires: [INotebookTracker],
  activate: (app: JupyterFrontEnd, tracker: INotebookTracker) => {
    // send start message
    console.log('JupyterLab extension jupyter-ra-extension is activated!');

    // define helper functions
    const insertText = (text: string) => {
      const current = tracker.currentWidget;
      const notebook = current!.content;
      const activeCell = notebook.activeCell;

      activeCell!.editor!.replaceSelection!(text);
    };

    // register commands
    app.commands.addCommand('ratui:text1', {
      label: 'RA:',
      caption: 'Relationale Algebra',
      isEnabled: () => false,
      execute: () => {}
    });

    app.commands.addCommand('ratui:projection', {
      label: 'π',
      caption: 'Projektion:\nπ a, b (R)\nAlternativ: pi',
      execute: () => insertText('π')
    });
    app.commands.addCommand('ratui:selection', {
      label: 'σ',
      caption: 'Selektion:\nσ a=1 (R)\nAlternativ: sigma',
      execute: () => insertText('σ')
    });
    app.commands.addCommand('ratui:rename', {
      label: 'β',
      caption: 'Umbenennung:\nβ a←b (R)\nAlternativ: beta',
      execute: () => insertText('β')
    });
    app.commands.addCommand('ratui:cross', {
      label: '×',
      caption: 'Kreuzprodukt:\nR × S',
      execute: () => insertText('×')
    });
    app.commands.addCommand('ratui:join', {
      label: '⋈',
      caption: 'Natürlicher Verbund:\nR ⋈ S\nAlternativ: join',
      execute: () => insertText('⋈')
    });
    app.commands.addCommand('ratui:left-outer-join', {
      label: '⟕',
      caption: 'Left Outer Join:\nR ⟕ S\nAlternativ: ljoin',
      execute: () => insertText('⟕')
    });
    app.commands.addCommand('ratui:right-outer-join', {
      label: '⟖',
      caption: 'Right Outer Join:\nR ⟖ S\nAlternativ: rjoin',
      execute: () => insertText('⟖')
    });
    app.commands.addCommand('ratui:full-outer-join', {
      label: '⟗',
      caption: 'Full Outer Join:\nR ⟗ S\nAlternativ: fjoin, ojoin',
      execute: () => insertText('⟗')
    });
    app.commands.addCommand('ratui:union', {
      label: '∪',
      caption: 'Vereinigung:\nR ∪ S\nAlternativ: cup',
      execute: () => insertText('∪')
    });
    app.commands.addCommand('ratui:intersection', {
      label: '∩',
      caption: 'Schnitt:\nR ∩ S\nAlternativ: cap',
      execute: () => insertText('∩')
    });
    app.commands.addCommand('ratui:difference', {
      label: '-',
      caption: 'Differenz:\nR - S\nAlternativ: \\',
      execute: () => insertText('-')
    });
    app.commands.addCommand('ratui:division', {
      label: '÷',
      caption: 'Division:\nR ÷ S\nAlternativ: :',
      execute: () => insertText('÷')
    });

    app.commands.addCommand('ratui:text2', {
      label: '|',
      isEnabled: () => false,
      execute: () => {}
    });

    app.commands.addCommand('ratui:arrowleft', {
      label: '←',
      caption: 'Alternativ: <-',
      execute: () => insertText('←')
    });

    app.commands.addCommand('ratui:text3', {
      label: '|',
      isEnabled: () => false,
      execute: () => {}
    });

    app.commands.addCommand('ratui:and', {
      label: '∧',
      caption: 'Alternativ: and',
      execute: () => insertText('∧')
    });
    app.commands.addCommand('ratui:or', {
      label: '∨',
      caption: 'Alternativ: or',
      execute: () => insertText('∨')
    });
    app.commands.addCommand('ratui:not', {
      label: '¬',
      caption: 'Alternativ: !',
      execute: () => insertText('¬')
    });

    app.commands.addCommand('ratui:text4', {
      label: '|',
      isEnabled: () => false,
      execute: () => {}
    });

    app.commands.addCommand('ratui:equal', {
      label: '=',
      execute: () => insertText('=')
    });
    app.commands.addCommand('ratui:unequal', {
      label: '≠',
      caption: 'Alternativ: !=',
      execute: () => insertText('≠')
    });
    app.commands.addCommand('ratui:lt', {
      label: '<',
      execute: () => insertText('<')
    });
    app.commands.addCommand('ratui:lte', {
      label: '≤',
      caption: 'Alternativ: <=',
      execute: () => insertText('≤')
    });
    app.commands.addCommand('ratui:gte', {
      label: '≥',
      caption: 'Alternativ: >=',
      execute: () => insertText('≥')
    });
    app.commands.addCommand('ratui:gt', {
      label: '>',
      execute: () => insertText('>')
    });
  }
};

export default plugin;
