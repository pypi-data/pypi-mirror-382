import { JupyterFrontEnd } from '@jupyterlab/application';
import { INotebookTracker } from '@jupyterlab/notebook';
import {
  ICommandPalette,
  IThemeManager,
  IToolbarWidgetRegistry,
  WidgetTracker
} from '@jupyterlab/apputils';
import { IStateDB } from '@jupyterlab/statedb';
import { IDocumentManager } from '@jupyterlab/docmanager';
import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { CachingService, SETTING_KEYS } from './utils/caching';
import { StateDBCachingService } from './utils/backendCaching';
import { AppStateService } from './AppState';
import { ListModel } from '@jupyterlab/extensionmanager';
import { ConfigService } from './Config/ConfigService';
import { ToolService } from './Services/ToolService';
import { PlanStateDisplay } from './Components/PlanStateDisplay';
import { LLMStateDisplay } from './Components/LLMStateDisplay';
import { WaitingUserReplyBoxManager } from './Notebook/WaitingUserReplyBoxManager';
import { NotebookContextManager } from './Notebook/NotebookContextManager';
import { ActionHistory } from './Chat/ActionHistory';
import { NotebookTools } from './Notebook/NotebookTools';
import { CellTrackingService } from './CellTrackingService';
import { TrackingIDUtility } from './TrackingIDUtility';
import { ContextCellHighlighter } from './Chat/ChatContextMenu/ContextCellHighlighter';
import { TabCompletionService } from './Services/TabCompletionService';
import { CompletionManager } from './Services/CompletionManager';
import { DatabaseMetadataCache } from './Services/DatabaseMetadataCache';
import { ContextCacheService } from './Chat/ChatContextMenu/ContextCacheService';
import { KernelExecutionListener } from './Chat/ChatContextMenu/KernelExecutionListener';
import { NotebookDiffManager } from './Notebook/NotebookDiffManager';
import { NotebookDiffTools } from './Notebook/NotebookDiffTools';
import { v4 as uuidv4 } from 'uuid';
import { Widget } from '@lumino/widgets';
import { NotebookSettingsContainer } from './NotebookSettingsContainer';
import { SnippetCreationWidget } from './Components/SnippetCreationWidget';
import { DiffNavigationWidget } from './Components/DiffNavigationWidget';
import { DatabaseManagerWidget } from './Components/DatabaseManagerWidget/DatabaseManagerWidget';
import { FileExplorerWidget } from './Components/FileExplorerWidget';
import { NotebookChatContainer } from './Notebook/NotebookChatContainer';
import { KernelUtils } from './utils/kernelUtils';
import { registerCommands } from './commands';
import { registerEvalCommands } from './eval_commands';
import { addIcon } from '@jupyterlab/ui-components';
import { JupyterFrontEndPlugin } from '@jupyterlab/application';
import {
  getGlobalDiffNavigationWidget,
  getGlobalSnippetCreationWidget,
  setGlobalDiffNavigationWidget,
  setGlobalSnippetCreationWidget
} from './globalWidgets';
import { JWTAuthModalService } from './Services/JWTAuthModalService';
import { JupyterAuthService } from './Services/JupyterAuthService';
import { JwtTokenDialog, MessageDialog } from './Components/JwtTokenDialog';
import { SettingsWidget } from './Components/Settings/SettingsWidget';

export async function activateSage(
  app: JupyterFrontEnd,
  notebooks: INotebookTracker,
  palette: ICommandPalette,
  themeManager: IThemeManager,
  db: IStateDB,
  documentManager: IDocumentManager,
  settingRegistry: ISettingRegistry | null,
  toolbarRegistry: IToolbarWidgetRegistry | null,
  plugin: JupyterFrontEndPlugin<void>
) {
  console.log('JupyterLab extension signalpilot-ai-internal is activated!');

  // Initialize the caching service with settings registry
  CachingService.initialize(settingRegistry);

  // Initialize the state database caching service for chat histories
  StateDBCachingService.initialize();

  // Initialize the database state service with StateDB (async, non-blocking)
  console.log('[Plugin] Initializing database state service...');
  import('./DatabaseStateService').then(({ DatabaseStateService }) => {
    DatabaseStateService.initializeWithStateDB().catch(error => {
      console.warn(
        '[Plugin] Database state service initialization failed:',
        error
      );
    });
  });

  // Initialize JWT authentication immediately on startup (CRITICAL: Do this early!)
  console.log('[Plugin] Initializing JWT authentication on startup...');
  try {
    const jwtInitialized = await JWTAuthModalService.initializeJWTOnStartup();
    if (jwtInitialized) {
      console.log(
        '[Plugin] JWT authentication initialized successfully on startup'
      );
    } else {
      console.log('[Plugin] No JWT token found during startup initialization');
    }
  } catch (error) {
    console.error('[Plugin] Failed to initialize JWT on startup:', error);
  }

  // Load snippets from StateDB (async, non-blocking)
  AppStateService.loadSnippets().catch(error => {
    console.warn('[Plugin] Failed to load snippets from StateDB:', error);
  });

  // Load inserted snippets from StateDB (async, non-blocking)
  AppStateService.loadInsertedSnippets().catch(error => {
    console.warn(
      '[Plugin] Failed to load inserted snippets from StateDB:',
      error
    );
  });

  const moveToChatHistory = async () => {
    const oldHistories = await CachingService.getSetting(
      SETTING_KEYS.CHAT_HISTORIES,
      {}
    );
    if (oldHistories && Object.keys(oldHistories).length > 0) {
      console.log('MOVING ALL SETTINGS TO THE STATE DB');
      await StateDBCachingService.setValue(
        SETTING_KEYS.CHAT_HISTORIES,
        oldHistories
      );
      console.log('SUCCESSFULLY MOVED ALL SETTINGS TO THE STATE DB');

      await CachingService.setSetting(SETTING_KEYS.CHAT_HISTORIES, {});
    }
  };

  moveToChatHistory();

  // Store settings registry in AppState
  AppStateService.setSettingsRegistry(settingRegistry);

  const loadSettingsRegistry = async () => {
    if (!settingRegistry) return;
    const settings = await settingRegistry.load(plugin.id);
  };

  const serviceManager = app.serviceManager;

  // Store service manager in AppState
  AppStateService.setServiceManager(serviceManager);

  const extensions = new ListModel(serviceManager as any);

  // Store extensions in AppState for UpdateBanner to use
  AppStateService.setExtensions(extensions);

  const contentManager = app.serviceManager.contents;

  // Replace localStorage with settings registry for theme flag
  const checkAndSetTheme = async () => {
    const alreadySet = await CachingService.getBooleanSetting(
      SETTING_KEYS.DARK_THEME_APPLIED,
      false
    );
    if (!alreadySet) {
      console.log('Setting theme to JupyterLab Dark (first time)');
      themeManager.setTheme('JupyterLab Dark');
      await CachingService.setBooleanSetting(
        SETTING_KEYS.DARK_THEME_APPLIED,
        true
      );
    }
  };
  checkAndSetTheme();

  // Ensure 'data' directory exists and create 'example.csv' if missing
  const ensureDataDirAndFile = async () => {
    try {
      // Check if 'data' directory exists
      let dirExists = false;
      try {
        const dir = await contentManager.get('data');
        dirExists = dir.type === 'directory';
      } catch (e) {
        dirExists = false;
      }
      if (!dirExists) {
        // Create untitled directory, then rename to 'data'
        const untitledDir = await contentManager.newUntitled({
          type: 'directory',
          path: ''
        });
        await contentManager.rename(untitledDir.path, 'data');
        console.log("Created 'data' directory.");
      }
      // Check if 'example.csv' exists
      let fileExists = false;
      try {
        await contentManager.get('data/example.csv');
        fileExists = true;
      } catch (e) {
        fileExists = false;
      }
      if (!fileExists) {
        await contentManager.save('data/example.csv', {
          type: 'file',
          format: 'text',
          content:
            'Date,Open,High,Low,Close,Volume,Symbol\n' +
            '2024-01-02,473.25,478.90,471.15,477.71,82145600,SPY\n' +
            '2024-01-03,477.80,481.35,475.20,480.92,73892400,SPY'
        });
        console.log("Created 'data/example.csv' with S&P 500 sample data.");
      }
    } catch (err) {
      console.error('Error ensuring data directory and example.csv:', err);
    }
  };
  ensureDataDirAndFile();

  // Load settings if available
  if (settingRegistry) {
    settingRegistry
      .load(plugin.id)
      .then(settings => {
        console.log('Loaded settings for signalpilot-ai-internal');
        const defaultService = settings.get('defaultService')
          .composite as string;
        // Store the default service in ConfigService
        if (defaultService) {
          ConfigService.setActiveModelType(defaultService);
        }

        // Watch for setting changes
        settings.changed.connect(() => {
          const newDefaultService = settings.get('defaultService')
            .composite as string;
          ConfigService.setActiveModelType(newDefaultService);
          console.log(`Default service changed to ${newDefaultService}`);
        });
      })
      .catch(error => {
        console.error('Failed to load settings for signalpilot-ai-internal', error);
      });
  }

  // Create a shared ToolService instance that has access to the notebook context
  const toolService = new ToolService();

  const planStateDisplay = new PlanStateDisplay();
  const llmStateDisplay = new LLMStateDisplay();
  const waitingUserReplyBoxManager = new WaitingUserReplyBoxManager();

  // Set the did y tracker in the tool service
  toolService.setNotebookTracker(notebooks, waitingUserReplyBoxManager);

  // Set the content manager in the tool service
  toolService.setContentManager(contentManager);

  // Initialize NotebookContextManager with the shared tool service
  const notebookContextManager = new NotebookContextManager(toolService);

  // Set the context manager in the tool service
  toolService.setContextManager(notebookContextManager);

  // Initialize action history
  const actionHistory = new ActionHistory();

  // Initialize NotebookTools
  const notebookTools = new NotebookTools(
    notebooks,
    waitingUserReplyBoxManager
  );

  // Initialize the AppState with core services
  AppStateService.initializeCoreServices(
    toolService,
    notebooks,
    notebookTools,
    notebookContextManager,
    contentManager,
    settingRegistry
  );

  // Initialize managers in AppState
  AppStateService.initializeManagers(
    planStateDisplay,
    llmStateDisplay,
    waitingUserReplyBoxManager
  );

  // Initialize additional services
  AppStateService.initializeAdditionalServices(
    actionHistory,
    new CellTrackingService(notebookTools, notebooks),
    new TrackingIDUtility(notebooks),
    new ContextCellHighlighter(notebooks, notebookContextManager, notebookTools)
  );

  // Initialize tab completion service (async, non-blocking)
  const tabCompletionService = TabCompletionService.getInstance();
  tabCompletionService.initialize().catch(error => {
    console.warn(
      '[Plugin] Tab completion service initialization failed:',
      error
    );
  });

  // Initialize completion manager
  const completionManager = CompletionManager.getInstance();
  completionManager.initialize(notebooks);

  // Initialize database metadata cache (async, non-blocking)
  const databaseCache = DatabaseMetadataCache.getInstance();
  databaseCache.initializeOnStartup().catch(error => {
    console.warn('[Plugin] Database cache initialization failed:', error);
  });

  // Initialize context cache service (async, non-blocking)
  const contextCacheService = ContextCacheService.getInstance();

  // Initialize kernel execution listener (async, non-blocking)
  const kernelExecutionListener = KernelExecutionListener.getInstance();

  // Set up a delayed initialization to ensure all core services are ready
  setTimeout(async () => {
    try {
      await contextCacheService.initialize();
      console.log('[Plugin] Context cache service initialized');

      // Initialize kernel execution listener after context cache service
      await kernelExecutionListener.initialize(notebooks);
      console.log('[Plugin] Kernel execution listener initialized');

      // Start initial context loading (non-blocking)
      contextCacheService.loadAllContexts().catch(error => {
        console.warn('[Plugin] Initial context loading failed:', error);
      });

      // Subscribe to notebook changes for context refreshing
      contextCacheService.subscribeToNotebookChanges();
    } catch (error) {
      console.warn(
        '[Plugin] Context cache service initialization failed:',
        error
      );
    }
  }, 1000); // Wait 1 second for core services to be ready

  // Initialize CellTrackingService - now retrieved from AppState
  const cellTrackingService = AppStateService.getCellTrackingService();

  // Initialize ContextCellHighlighter - now retrieved from AppState
  const contextCellHighlighter = AppStateService.getContextCellHighlighter();

  // Initialize NotebookDiffManager
  const diffManager = new NotebookDiffManager(notebookTools, actionHistory);

  // Update AppState with the diff manager
  AppStateService.setState({ notebookDiffManager: diffManager });

  // Initialize diff2html theme detection
  NotebookDiffTools.initializeThemeDetection();

  // Set up notebook tracking to provide the active notebook widget to the diffManager
  notebooks.currentChanged.connect(async (_, notebook) => {
    if (notebook) {
      const nbFile = await contentManager.get(notebook.context.path);
      let notebookUniqueId: string | null = null;

      console.log('================== NEW NOTEBOOK FILE =================');
      console.log(nbFile);

      if (nbFile && nbFile.content) {
        // get notebook metadata
        if (!nbFile.content.metadata || !nbFile.content.nbformat) return;

        const nbMetadata = nbFile.content.metadata || {};

        if (!nbMetadata.sage_ai || !nbMetadata.sage_ai.unique_id) {
          await notebook.context.save();
          nbMetadata.sage_ai = {
            unique_id: 'nb_' + uuidv4() + '_' + Date.now()
          };

          nbFile.content.metadata = nbMetadata;
          if (nbFile.content.metadata) {
            // only save if metadata exists
            await contentManager.save(notebook.context.path, nbFile);
          }

          await notebook.context.revert();
          await notebook.context.save();
        }

        notebookUniqueId = nbMetadata.sage_ai.unique_id;
      }

      let oldPath = notebook.context.path;

      notebook.context.pathChanged.connect(async (_, path) => {
        if (oldPath !== path) {
          // Get the unique_id from notebook metadata to use as the notebook ID
          try {
            console.log('RENAMING NOTEBOOK');
            const updatedNbFile = await contentManager.get(path);
            const currentNotebookId =
              updatedNbFile?.content?.metadata?.sage_ai?.unique_id ||
              notebookUniqueId;

            console.log('NB ID:', currentNotebookId);

            if (currentNotebookId) {
              // Update the centralized notebook ID in AppStateService using unique_id
              // Services will automatically respond to the events from AppStateService
              AppStateService.setCurrentNotebook(notebook, notebookUniqueId);
              AppStateService.updateNotebookId(
                notebookUniqueId || oldPath,
                currentNotebookId
              );
              notebookUniqueId = currentNotebookId;
            }
          } catch (error) {
            console.warn(
              'Could not get notebook metadata after path change:',
              error
            );
            // Fallback to path-based update for backward compatibility
            AppStateService.setCurrentNotebook(notebook, notebookUniqueId);
            AppStateService.updateNotebookId(oldPath, path);
          }

          oldPath = path;
        }
      });

      for (const cell of notebook.content.widgets) {
        NotebookDiffTools.removeDiffOverlay(cell);
      }

      diffManager.setNotebookWidget(notebook);

      // Set the current notebook and ID using the unique_id
      if (notebookUniqueId) {
        AppStateService.setCurrentNotebook(notebook, notebookUniqueId);
        AppStateService.getState().chatContainer?.chatWidget.cancelMessage();
      } else {
        // Fallback to just setting the notebook without an ID
        AppStateService.setCurrentNotebook(notebook);
      }

      // Initialize tracking metadata for existing cells
      cellTrackingService.initializeExistingCells();
    }
  });

  // Initialize the tracking ID utility - now retrieved from AppState
  const trackingIDUtility = AppStateService.getTrackingIDUtility();

  // Create the widget tracker
  const tracker = new WidgetTracker<Widget>({
    namespace: 'sage-ai-widgets'
  });

  // Initialize the containers
  let settingsContainer: NotebookSettingsContainer | undefined;
  let snippetCreationWidget: SnippetCreationWidget | undefined;
  let diffNavigationWidget: DiffNavigationWidget | undefined;
  let databaseManagerWidget: DatabaseManagerWidget | undefined;
  let fileExplorerWidget: FileExplorerWidget | undefined;

  const initializeChatContainer = async () => {
    // Get existing chat container from AppState
    const existingChatContainer = AppStateService.getState().chatContainer;

    // Create a new chat container
    const createContainer = async () => {
      console.log('[Plugin] Creating new NotebookChatContainer');
      // Pass the shared tool service, diff manager, and notebook context manager to the container
      const newContainer = new NotebookChatContainer(
        toolService,
        notebookContextManager,
        actionHistory
      );
      await tracker.add(newContainer);

      // Add the container to the right side panel
      app.shell.add(newContainer, 'right', { rank: 1000, activate: true }); // Activate the chat container to make it visible and expanded by default

      // If there's a current notebook, set its path
      if (notebooks.currentWidget) {
        // Use the centralized notebook ID from AppStateService
        const currentNotebookId = AppStateService.getCurrentNotebookId();
        if (currentNotebookId) {
          await newContainer.switchToNotebook(currentNotebookId);
        } else {
          // Try to get unique_id from current notebook metadata first
          try {
            const nbFile = await contentManager.get(
              notebooks.currentWidget.context.path
            );
            const notebookUniqueId =
              nbFile?.content?.metadata?.sage_ai?.unique_id;
            if (notebookUniqueId) {
              await newContainer.switchToNotebook(notebookUniqueId);
            } else {
              // Fallback to path if unique_id not available
              await newContainer.switchToNotebook(
                notebooks.currentWidget.context.path
              );
            }
          } catch (error) {
            console.warn(
              'Could not get notebook metadata in initializeChatContainer:',
              error
            );
            // Fallback to path if metadata retrieval fails
            await newContainer.switchToNotebook(
              notebooks.currentWidget.context.path
            );
          }
        }
      }

      // Store in AppState
      AppStateService.setChatContainer(newContainer);

      return newContainer;
    };

    if (!existingChatContainer || existingChatContainer.isDisposed) {
      const chatContainer = await createContainer();

      // Set the chat container reference in the context cell highlighter
      contextCellHighlighter.setChatContainer(chatContainer);

      void app.restored.then(() => {
        app.shell.activateById('sage-ai-chat-container');
        
        // Auto-render the welcome CTA after chat container is loaded
        // Use a small delay to ensure the chat widget is fully initialized
        setTimeout(() => {
          if (notebooks.currentWidget) {
            app.commands.execute('sage-ai:add-cta-div').catch((error) => {
              console.warn('[Plugin] Failed to auto-render welcome CTA:', error);
            });
          }
        }, 300);
      });

      return chatContainer;
    }

    return existingChatContainer;
  };

  const initializeSettingsContainer = () => {
    // Create a new settings container
    const createContainer = () => {
      // Pass the shared tool service, diff manager, and notebook context manager to the container
      const newContainer = new NotebookSettingsContainer(
        toolService,
        diffManager,
        notebookContextManager
      );
      tracker.add(newContainer);

      // Add the container to the right side panel
      app.shell.add(newContainer, 'right', { rank: 1001 });

      return newContainer;
    };

    if (!settingsContainer || settingsContainer.isDisposed) {
      settingsContainer = createContainer();
    }

    return settingsContainer;
  };

  const initializeSnippetCreationWidget = () => {
    // Create a new snippet creation widget
    const createWidget = () => {
      const newWidget = new SnippetCreationWidget();
      tracker.add(newWidget);

      // Add the widget to the left side panel
      app.shell.add(newWidget, 'left', { rank: 1000 });

      return newWidget;
    };

    if (!snippetCreationWidget || snippetCreationWidget.isDisposed) {
      snippetCreationWidget = createWidget();
    }

    return snippetCreationWidget;
  };

  const initializeFileExplorerWidget = () => {
    // Create a new file explorer widget
    const createWidget = () => {
      const newWidget = new FileExplorerWidget();

      // Set the app instance for file browser operations
      newWidget.setApp(app);

      tracker.add(newWidget);

      // Add the widget to the left side panel with a different rank
      app.shell.add(newWidget, 'left', { rank: 1001 });

      return newWidget;
    };

    if (!fileExplorerWidget || fileExplorerWidget.isDisposed) {
      fileExplorerWidget = createWidget();
    }

    return fileExplorerWidget;
  };

  const initializeDiffNavigationWidget = () => {
    // Create a new diff navigation widget
    const createWidget = () => {
      const newWidget = new DiffNavigationWidget();
      tracker.add(newWidget);

      // Append to current notebook only - do not create widget if no notebook
      const currentNotebook = notebooks.currentWidget;
      if (currentNotebook) {
        // Find the notebook panel element with the specified classes
        const notebookElement =
          currentNotebook.node.querySelector('.jp-Notebook');
        if (notebookElement) {
          notebookElement.appendChild(newWidget.node);
        } else {
          // Fallback to notebook panel if .jp-Notebook not found
          currentNotebook.node.appendChild(newWidget.node);
        }
      } else {
        // Do not create widget if no notebook is available
        console.log(
          'DiffNavigationWidget: No current notebook available, skipping widget creation'
        );
        return null;
      }

      return newWidget;
    };

    if (!diffNavigationWidget || diffNavigationWidget.isDisposed) {
      const newWidget = createWidget();
      if (newWidget) {
        diffNavigationWidget = newWidget;
      }
    }

    return diffNavigationWidget;
  };

  const initializeDatabaseManagerWidget = () => {
    // Create a new database manager widget
    const createWidget = () => {
      const newWidget = new DatabaseManagerWidget();
      tracker.add(newWidget);

      // Add the widget to the left side panel
      app.shell.add(newWidget, 'left', { rank: 1001 });

      return newWidget;
    };

    if (!databaseManagerWidget || databaseManagerWidget.isDisposed) {
      databaseManagerWidget = createWidget();
    }

    return databaseManagerWidget;
  };

  // Initialize all containers
  void initializeChatContainer();
  settingsContainer = initializeSettingsContainer();
  snippetCreationWidget = initializeSnippetCreationWidget();
  fileExplorerWidget = initializeFileExplorerWidget();
  diffNavigationWidget = initializeDiffNavigationWidget();
  databaseManagerWidget = initializeDatabaseManagerWidget();

  // Store widget references in AppState for global access
  AppStateService.setState({
    fileExplorerWidget,
    databaseManagerWidget,
    diffNavigationWidget
  });

  // Store widget references globally for cleanup
  setGlobalSnippetCreationWidget(snippetCreationWidget);
  setGlobalDiffNavigationWidget(diffNavigationWidget);

  // Initialize JWT authentication check - show modal if user is not authenticated
  const jwtModalService = JWTAuthModalService.getInstance();

  // Listen for settings widget state changes to detect authentication
  if (settingsContainer) {
    const settingsWidget = settingsContainer.getSettingsWidget();
    settingsWidget.stateChanged.connect(() => {
      const state = settingsWidget.getState();
      if (state.isAuthenticated) {
        // User has authenticated, hide the JWT modal if it's showing
        jwtModalService.checkAndHideIfAuthenticated();
      }
    });
  }

  // Check authentication status after initialization
  void app.restored.then(async () => {
    // Wait a bit for everything to settle, then check authentication
    setTimeout(async () => {
      await jwtModalService.showIfNeeded();
    }, 1000);
  });

  // Register DiffNavigationWidget with AppStateService
  if (diffNavigationWidget) {
    AppStateService.setDiffNavigationWidget(diffNavigationWidget);
  }

  // Set up DiffNavigationWidget to respond to notebook changes
  AppStateService.onNotebookChanged().subscribe(({ newNotebookId }) => {
    const globalDiffNavigationWidget = getGlobalDiffNavigationWidget();
    if (globalDiffNavigationWidget && !globalDiffNavigationWidget.isDisposed) {
      globalDiffNavigationWidget.setNotebookId(newNotebookId);

      // Re-attach widget to the new notebook (only if notebook exists)
      const currentNotebook = notebooks.currentWidget;
      if (currentNotebook && globalDiffNavigationWidget.node.parentNode) {
        // Remove from current parent
        globalDiffNavigationWidget.node.parentNode.removeChild(
          globalDiffNavigationWidget.node
        );

        // Find the notebook panel element and re-attach
        const notebookElement =
          currentNotebook.node.querySelector('.jp-Notebook');
        if (notebookElement) {
          notebookElement.appendChild(globalDiffNavigationWidget.node);
        } else {
          // Fallback to notebook panel if .jp-Notebook not found
          currentNotebook.node.appendChild(globalDiffNavigationWidget.node);
        }
      } else if (!currentNotebook) {
        // If no notebook available, remove widget from DOM but don't dispose
        if (globalDiffNavigationWidget.node.parentNode) {
          globalDiffNavigationWidget.node.parentNode.removeChild(
            globalDiffNavigationWidget.node
          );
        }
      }
    } else if (!globalDiffNavigationWidget && newNotebookId) {
      // Try to create widget if one doesn't exist and we have a notebook
      const newDiffWidget = initializeDiffNavigationWidget();
      setGlobalDiffNavigationWidget(newDiffWidget);
      if (newDiffWidget) {
        AppStateService.setDiffNavigationWidget(newDiffWidget);
      }
    }
  });

  // Set up notebook tracking to switch to the active notebook
  notebooks.currentChanged.connect(async (_, notebook) => {
    if (notebook) {
      // Fix for old notebooks having undeletable first cells
      if (notebook.model && notebook.model.cells.length > 0) {
        notebook.model.cells.get(0).setMetadata('deletable', true);
      }

      // Get the unique_id from notebook metadata to use as the notebook ID
      let notebookUniqueId: string | null = null;
      try {
        const nbFile = await contentManager.get(notebook.context.path);
        if (nbFile?.content?.metadata?.sage_ai?.unique_id) {
          notebookUniqueId = nbFile.content.metadata.sage_ai.unique_id;
        }
      } catch (error) {
        console.warn(
          'Could not get notebook metadata in currentChanged handler:',
          error
        );
      }

      // Set the current notebook ID in the centralized AppStateService using unique_id
      // Services that need to respond to notebook changes will subscribe to AppStateService events
      AppStateService.setCurrentNotebookId(
        notebookUniqueId || notebook.context.path
      );

      diffManager.setNotebookWidget(notebook);
      // Initialize tracking metadata for existing cells
      cellTrackingService.initializeExistingCells();

      const planCell = notebookTools.getPlanCell(
        notebookUniqueId || notebook.context.path
      );

      if (planCell) {
        const currentStep =
          (planCell.model.sharedModel.getMetadata().custom as any)
            ?.current_step_string || '';
        const nextStep =
          (planCell.model.sharedModel.getMetadata().custom as any)
            ?.next_step_string || '';
        const source = planCell.model.sharedModel.getSource() || '';

        void AppStateService.getPlanStateDisplay().updatePlan(
          currentStep || 'Plan active',
          nextStep,
          source,
          false
        );
      }

      notebook?.model?.cells.changed.connect(async () => {
        // Update the context cell highlighting when cells change
        trackingIDUtility.fixTrackingIDs(
          notebookUniqueId || notebook.context.path
        );
        contextCellHighlighter.refreshHighlighting(notebook);

        // Refresh cell contexts when cells change (async, non-blocking)
        setTimeout(() => {
          const contextCacheService = ContextCacheService.getInstance();
          contextCacheService.loadContextCategory('cells').catch(error => {
            console.warn('[Plugin] Cell context refresh failed:', error);
          });
        }, 200); // Small delay to let cell changes settle

        const planCell = notebookTools.getPlanCell(
          notebookUniqueId || notebook.context.path
        );

        if (planCell) {
          const currentStep =
            (planCell.model.sharedModel.getMetadata().custom as any)
              ?.current_step_string || '';
          const nextStep =
            (planCell.model.sharedModel.getMetadata().custom as any)
              ?.next_step_string || '';
          const source = planCell.model.sharedModel.getSource() || '';

          console.log('Updating step floating box', currentStep, nextStep);

          void AppStateService.getPlanStateDisplay().updatePlan(
            currentStep,
            nextStep,
            source,
            false
          );
        } else if (!planCell) {
          void AppStateService.getPlanStateDisplay().updatePlan(
            undefined,
            undefined,
            undefined
          );
        }

        if (notebook.model?.cells) {
          for (const cell of notebook.model.cells) {
            cell.metadataChanged.connect(() => {
              // Refresh the context cell highlighting when metadata changes
              contextCellHighlighter.refreshHighlighting(notebook);
            });
          }
        }
      });

      // Set database environment variables for all configured databases in the new notebook's kernel
      // Use retry mechanism since kernel might not be ready immediately
      console.log('[Plugin] Notebook changed, setting up database environments in kernel');
      KernelUtils.setDatabaseEnvironmentsInKernelWithRetry();

      // Refresh context cache on notebook switch (async, non-blocking)
      setTimeout(() => {
        const contextCacheService = ContextCacheService.getInstance();
        contextCacheService.refreshIfStale().catch(error => {
          console.warn(
            '[Plugin] Context refresh on notebook change failed:',
            error
          );
        });
      }, 500); // Small delay to let notebook setup complete

      // Notify database cache that kernel may be ready
      const databaseCache = DatabaseMetadataCache.getInstance();

      // Wait a bit for kernel setup to complete, then notify cache
      setTimeout(() => {
        console.log(
          '[Plugin] Notifying database cache of potential kernel readiness'
        );
        databaseCache.onKernelReady().catch(error => {
          console.warn(
            '[Plugin] Database cache kernel ready notification failed:',
            error
          );
        });
      }, 3000); // Wait 3 seconds for kernel to be fully ready

      // Add debugging functions to window for troubleshooting
      (window as any).debugDBURL = {
        // Legacy single DB URL functions (deprecated)
        check: () => KernelUtils.checkDbUrlInKernel(),
        debug: () => KernelUtils.debugAppStateDatabaseUrl(),
        set: (url?: string) => KernelUtils.setDbUrlInKernel(url),
        retry: () => KernelUtils.setDbUrlInKernelWithRetry(),
        // New multi-database environment functions
        setAllDatabases: () => KernelUtils.setDatabaseEnvironmentsInKernel(),
        retryAllDatabases: () => KernelUtils.setDatabaseEnvironmentsInKernelWithRetry()
      };

      // Add database cache debugging functions
      (window as any).debugDBCache = {
        getStatus: () => databaseCache.getCacheStatus(),
        refresh: () => databaseCache.refreshMetadata(),
        clear: () => databaseCache.clearCache(),
        onKernelReady: () => databaseCache.onKernelReady(),
        onSettingsChanged: () => databaseCache.onSettingsChanged()
      };

      // Add context cache debugging functions
      (window as any).debugContextCache = {
        getContexts: () => contextCacheService.getContexts(),
        refresh: () => contextCacheService.forceRefresh(),
        refreshCategory: (category: string) =>
          contextCacheService.loadContextCategory(category),
        refreshVariables: () =>
          contextCacheService.refreshVariablesAfterExecution(),
        getCacheAge: () => AppStateService.getContextCacheAge(),
        shouldRefresh: () => AppStateService.shouldRefreshContexts(),
        isLoading: () => AppStateService.isContextLoading()
      };

      // Add kernel execution listener debugging functions
      (window as any).debugKernelListener = {
        getDebugInfo: () => kernelExecutionListener.getDebugInfo(),
        triggerRefresh: () => kernelExecutionListener.triggerVariableRefresh(),
        dispose: () => kernelExecutionListener.dispose(),
        reinitialize: () => kernelExecutionListener.initialize(notebooks)
      };

      // Add login success modal debugging functions
      (window as any).debugLoginSuccess = {
        show: async () => {
          try {
            const { LoginSuccessModalService } = await import(
              './Services/LoginSuccessModalService'
            );
            LoginSuccessModalService.debugShow();
            console.log('✅ Login success modal triggered from debug');
          } catch (error) {
            console.error('❌ Failed to show login success modal:', error);
          }
        },
        getDebugInfo: async () => {
          try {
            const { LoginSuccessModalService } = await import(
              './Services/LoginSuccessModalService'
            );
            const instance = LoginSuccessModalService.getInstance();
            return instance.getDebugInfo();
          } catch (error) {
            console.error('❌ Failed to get debug info:', error);
            return null;
          }
        }
      };

      // Add JWT auth modal debugging functions
      (window as any).debugJWTAuth = {
        show: () => {
          jwtModalService.show();
          console.log('✅ JWT auth modal shown from debug');
        },
        hide: () => {
          jwtModalService.hide();
          console.log('✅ JWT auth modal hidden from debug');
        },
        forceShow: () => {
          jwtModalService.forceShow();
          console.log('✅ JWT auth modal force shown from debug');
        },
        checkAndHide: async () => {
          await jwtModalService.checkAndHideIfAuthenticated();
          console.log('✅ JWT auth modal check and hide completed');
        },
        getDebugInfo: async () => {
          return await jwtModalService.getDebugInfo();
        }
      };

      // Auto-render the welcome CTA on notebook switch
      // Use a small delay to ensure the notebook is fully set up
      setTimeout(() => {
        app.commands.execute('sage-ai:add-cta-div').catch((error) => {
          console.warn('[Plugin] Failed to auto-render welcome CTA on notebook switch:', error);
        });
      }, 300);
    }
  });

  // Register all commands
  registerCommands(app, palette);
  registerEvalCommands(app, palette, documentManager);

  // Set up notebook tracking to update button state
  notebooks.activeCellChanged.connect((_, cell) => {
    if (cell) {
      // Get the current notebook ID from centralized AppStateService
      const notebookId = AppStateService.getCurrentNotebookId();
      if (!notebookId) return;

      // Check if the cell has tracking ID metadata
      const metadata = cell.model.sharedModel.getMetadata() || {};
      let trackingId = '';

      if (
        metadata &&
        typeof metadata === 'object' &&
        'cell_tracker' in metadata &&
        metadata.cell_tracker &&
        typeof metadata.cell_tracker === 'object' &&
        'trackingId' in metadata.cell_tracker
      ) {
        trackingId = String(metadata.cell_tracker.trackingId);
      }

      // Update the button state based on whether this cell is in context
      const isInContext = trackingId
        ? notebookContextManager.isCellInContext(notebookId, trackingId)
        : notebookContextManager.isCellInContext(notebookId, cell.model.id);

      // Find the button
      const buttonNode = document.querySelector(
        '.jp-ToolbarButtonComponent[data-command="sage-ai-add-to-context"]'
      );
      if (buttonNode) {
        if (isInContext) {
          // Set to "Remove from Chat" state
          buttonNode.classList.add('in-context');

          const icon = buttonNode.querySelector('.jp-icon3');
          if (icon) {
            // Create a minus icon
            const minusIcon =
              '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"><path fill="currentColor" d="M5 13v-2h14v2z"/></svg>';
            icon.innerHTML = minusIcon;
          }

          const textSpan = buttonNode.querySelector('.button-text');
          if (textSpan) {
            textSpan.textContent = 'Remove from Chat';
          }
        } else {
          // Set to "Add to Chat" state
          buttonNode.classList.remove('in-context');

          const icon = buttonNode.querySelector('.jp-icon3');
          if (icon) {
            icon.innerHTML = addIcon.svgstr;
          }

          const textSpan = buttonNode.querySelector('.button-text');
          if (textSpan) {
            textSpan.textContent = 'Add to Context';
          }
        }
      }
    }
  });

  const { commands } = app;

  const commandId = 'signalpilot-ai-internal:log-selected-code';
  palette.addItem({ command: commandId, category: 'SignalPilot AI' });
  app.commands.addKeyBinding({
    command: commandId,
    keys: ['Accel Shift K'],
    selector: '.jp-Notebook.jp-mod-editMode' // only trigger in edit mode
  });

  commands.addCommand(commandId, {
    label: 'Log Selected Code',
    execute: () => {
      const current = tracker.currentWidget;
      if (!current) {
        console.warn('No active notebook');
        return;
      }

      const activeCell = notebooks.activeCell;
      if (!activeCell) {
        console.warn('No active cell');
        return;
      }

      const editor = activeCell.editor;
      const selection = editor?.getSelection();
      if (selection) {
        console.log('Selection:', selection);
      } else {
        console.log('No selection');
      }

      const selectedText = editor?.model.sharedModel.source.substring(
        editor.getOffsetAt(selection?.start || { line: 0, column: 0 }),
        editor.getOffsetAt(selection?.end || { line: 0, column: 0 })
      );

      if (selectedText) {
        console.log('Selected text:', selectedText);
      } else {
        console.log('No text selected');
      }
    }
  });

  // Add command to open/toggle Snippet Creation Widget
  const snippetCommandId = 'signalpilot-ai-internal:open-snippet-creation';

  commands.addCommand(snippetCommandId, {
    label: 'Open Rule Creation',
    execute: () => {
      const globalSnippetCreationWidget = getGlobalSnippetCreationWidget();
      if (
        globalSnippetCreationWidget &&
        !globalSnippetCreationWidget.isDisposed
      ) {
        if (globalSnippetCreationWidget.getIsVisible()) {
          globalSnippetCreationWidget.hide();
        } else {
          globalSnippetCreationWidget.show();
          app.shell.activateById(globalSnippetCreationWidget.id);
        }
      }
    }
  });

  palette.addItem({ command: snippetCommandId, category: 'SignalPilot AI' });

  // Add command to activate test mode - allows setting JWT token directly
  const testModeCommandId = 'signalpilot-ai-internal:activate-test-mode';

  commands.addCommand(testModeCommandId, {
    label: 'Activate Test Mode (Set JWT Token)',
    execute: async () => {
      try {
        const jwtDialog = new JwtTokenDialog();
        const result = await jwtDialog.showDialog();

        if (result.accepted && result.value) {
          console.log('[Test Mode] Setting JWT token...');
          await JupyterAuthService.storeJwtToken(result.value);
          AppStateService.updateClaudeSettings({ claudeApiKey: result.value });

          console.log('[Test Mode] JWT token set successfully');

          // Show success message
          await MessageDialog.showMessage(
            'Test Mode',
            'JWT token has been set successfully in the state database.'
          );
        } else {
          console.log('[Test Mode] JWT token setting cancelled');
        }
      } catch (error) {
        console.error('[Test Mode] Failed to set JWT token:', error);

        const errorMessage =
          error instanceof Error ? error.message : String(error);

        // Show error message
        await MessageDialog.showMessage(
          'Test Mode - Error',
          `Failed to set JWT token: ${errorMessage}`,
          true
        );
      }
    }
  });

  palette.addItem({ command: testModeCommandId, category: 'SignalPilot AI' });

  return;
}
