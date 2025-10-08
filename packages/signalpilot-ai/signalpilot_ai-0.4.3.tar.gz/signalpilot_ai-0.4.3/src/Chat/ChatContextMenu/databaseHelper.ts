/**
 * Database helper utilities for context menu integration
 */
import { DatabaseStateService, IDatabaseConfig, DatabaseType } from '../../DatabaseStateService';
import { MentionContext } from './ChatContextLoaders';

/**
 * Interface for database context items in the context picker
 */
export interface DatabaseContext extends MentionContext {
  type: 'database';
  databaseType: DatabaseType;
  connectionType: 'credentials' | 'url';
  isActive: boolean;
}

/**
 * Get database type display name
 */
function getDatabaseTypeDisplayName(type: DatabaseType): string {
  switch (type) {
    case DatabaseType.PostgreSQL:
      return 'PostgreSQL';
    case DatabaseType.MySQL:
      return 'MySQL';
    case DatabaseType.Snowflake:
      return 'Snowflake';
    default:
      return 'Database';
  }
}

/**
 * Get database description from configuration
 */
function getDatabaseDescription(config: IDatabaseConfig): string {
  if (config.connectionType === 'url' && config.urlConnection) {
    return config.urlConnection.description;
  } else if (config.connectionType === 'credentials' && config.credentials) {
    return config.credentials.description;
  }
  return '';
}

/**
 * Format database connection info for display
 */
function formatConnectionInfo(config: IDatabaseConfig): string {
  if (config.connectionType === 'url' && config.urlConnection) {
    // For URL connections, show partial URL for security
    const url = config.urlConnection.connectionUrl;
    if (url.includes('@')) {
      const parts = url.split('@');
      if (parts.length > 1) {
        return `Connection URL: ***@${parts[parts.length - 1]}`;
      }
    }
    return 'Connection URL: ***';
  } else if (config.connectionType === 'credentials' && config.credentials) {
    // For credential connections, show host and database
    return `Host: ${config.credentials.host}:${config.credentials.port}, Database: ${config.credentials.database}`;
  }
  return 'Database connection';
}

/**
 * Create database context content for the mention system
 */
function createDatabaseContextContent(config: IDatabaseConfig): string {
  const typeDisplayName = getDatabaseTypeDisplayName(config.type);
  const connectionInfo = formatConnectionInfo(config);
  
  let content = `Database: ${config.name}\n`;
  content += `Type: ${typeDisplayName}\n`;
  content += `Description: ${getDatabaseDescription(config) || 'No description provided'}\n`;
  content += `Connection: ${connectionInfo}\n`;
  
  if (config.connectionType === 'credentials' && config.credentials) {
    content += `Database Name: ${config.credentials.database}\n`;
    content += `Username: ${config.credentials.username}\n`;
    
    // Add Snowflake-specific info
    if (config.type === DatabaseType.Snowflake && 'connectionUrl' in config.credentials) {
      content += `Connection URL: ${config.credentials.connectionUrl}\n`;
      if (config.credentials.warehouse) {
        content += `Warehouse: ${config.credentials.warehouse}\n`;
      }
      if (config.credentials.role) {
        content += `Role: ${config.credentials.role}\n`;
      }
    }
  }
  
  content += `\nCreated: ${new Date(config.createdAt).toLocaleDateString()}\n`;
  content += `Updated: ${new Date(config.updatedAt).toLocaleDateString()}\n`;
  
  // Add usage instructions
  content += `\nUsage Instructions:\n`;
  content += `- This database connection is available in your Python environment\n`;
  content += `- Use standard database libraries like psycopg2, SQLAlchemy, or pandas to connect\n`;
  content += `- Connection details are securely stored and can be referenced by this configuration name\n`;
  
  return content;
}

/**
 * Get all database configurations as MentionContext items for the context picker
 * This function retrieves database configurations from DatabaseStateService
 * and formats them for use in the chat context menu
 * 
 * @returns Array of DatabaseContext items ready for the context picker
 */
export async function getDatabases(): Promise<DatabaseContext[]> {
  console.log('[DatabaseHelper] Loading database configurations...');
  
  try {
    // Get all database configurations from the service
    const configurations = DatabaseStateService.getConfigurations();
    const activeConfigId = DatabaseStateService.getState().activeConfigId;
    
    console.log(`[DatabaseHelper] Found ${configurations.length} database configurations`);
    
    // Convert database configs to context items
    const databaseContexts: DatabaseContext[] = configurations.map((config) => {
      const typeDisplayName = getDatabaseTypeDisplayName(config.type);
      const isActive = config.id === activeConfigId;
      
      // Create a concise description for the context picker
      let description = getDatabaseDescription(config) || `${typeDisplayName} database connection`;
      if (description.length > 80) {
        description = description.substring(0, 77) + '...';
      }
      
      // Add connection type and active status to description
      const statusInfo = [];
      if (isActive) {
        statusInfo.push('Active');
      }
      statusInfo.push(config.connectionType === 'url' ? 'URL Connection' : 'Credential Connection');
      
      if (statusInfo.length > 0) {
        description += ` (${statusInfo.join(', ')})`;
      }
      
      return {
        type: 'database' as const,
        id: `database-${config.id}`,
        name: config.name,
        description,
        content: createDatabaseContextContent(config),
        databaseType: config.type,
        connectionType: config.connectionType,
        isActive,
        isDirectory: false
      };
    });
    
    // Sort databases: active first, then by name
    databaseContexts.sort((a, b) => {
      if (a.isActive && !b.isActive) return -1;
      if (!a.isActive && b.isActive) return 1;
      return a.name.localeCompare(b.name);
    });
    
    console.log(`[DatabaseHelper] Converted ${databaseContexts.length} database contexts`);
    return databaseContexts;
    
  } catch (error) {
    console.error('[DatabaseHelper] Error loading database configurations:', error);
    return [];
  }
}

/**
 * Get a specific database configuration by ID for context usage
 * 
 * @param databaseId The database configuration ID (without 'database-' prefix)
 * @returns DatabaseContext item or null if not found
 */
export async function getDatabaseById(databaseId: string): Promise<DatabaseContext | null> {
  try {
    const config = DatabaseStateService.getConfiguration(databaseId);
    if (!config) {
      return null;
    }
    
    const activeConfigId = DatabaseStateService.getState().activeConfigId;
    const typeDisplayName = getDatabaseTypeDisplayName(config.type);
    const isActive = config.id === activeConfigId;
    
    let description = getDatabaseDescription(config) || `${typeDisplayName} database connection`;
    if (description.length > 80) {
      description = description.substring(0, 77) + '...';
    }
    
    return {
      type: 'database' as const,
      id: `database-${config.id}`,
      name: config.name,
      description,
      content: createDatabaseContextContent(config),
      databaseType: config.type,
      connectionType: config.connectionType,
      isActive,
      isDirectory: false
    };
    
  } catch (error) {
    console.error(`[DatabaseHelper] Error loading database ${databaseId}:`, error);
    return null;
  }
}

/**
 * Refresh database contexts - useful when database configurations change
 * This function can be called to invalidate any caching and reload fresh data
 * 
 * @returns Promise that resolves when refresh is complete
 */
export async function refreshDatabaseContexts(): Promise<void> {
  console.log('[DatabaseHelper] Refreshing database contexts...');
  // Since we're reading directly from DatabaseStateService, no caching to clear
  // This function serves as a placeholder for future caching mechanisms
  return Promise.resolve();
}

/**
 * Check if databases are available for context
 * 
 * @returns true if there are database configurations available
 */
export function hasDatabases(): boolean {
  const configurations = DatabaseStateService.getConfigurations();
  return configurations.length > 0;
}