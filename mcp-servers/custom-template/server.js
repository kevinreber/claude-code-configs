#!/usr/bin/env node

/**
 * Custom MCP Server Template
 *
 * This is a starting point for creating your own MCP server.
 * Modify this template to add custom tools for Claude to use.
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

// Create server instance
const server = new Server(
  {
    name: 'custom-server',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Define available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'hello_world',
        description: 'A simple hello world tool that greets the user',
        inputSchema: {
          type: 'object',
          properties: {
            name: {
              type: 'string',
              description: 'The name to greet',
            },
          },
          required: ['name'],
        },
      },
      {
        name: 'calculate',
        description: 'Perform a simple calculation',
        inputSchema: {
          type: 'object',
          properties: {
            operation: {
              type: 'string',
              enum: ['add', 'subtract', 'multiply', 'divide'],
              description: 'The operation to perform',
            },
            a: {
              type: 'number',
              description: 'First operand',
            },
            b: {
              type: 'number',
              description: 'Second operand',
            },
          },
          required: ['operation', 'a', 'b'],
        },
      },
      // Add more tools here
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  switch (name) {
    case 'hello_world': {
      const greeting = `Hello, ${args.name}! Welcome to the custom MCP server.`;
      return {
        content: [{ type: 'text', text: greeting }],
      };
    }

    case 'calculate': {
      const { operation, a, b } = args;
      let result;

      switch (operation) {
        case 'add':
          result = a + b;
          break;
        case 'subtract':
          result = a - b;
          break;
        case 'multiply':
          result = a * b;
          break;
        case 'divide':
          if (b === 0) {
            return {
              content: [{ type: 'text', text: 'Error: Division by zero' }],
              isError: true,
            };
          }
          result = a / b;
          break;
        default:
          return {
            content: [{ type: 'text', text: `Unknown operation: ${operation}` }],
            isError: true,
          };
      }

      return {
        content: [{ type: 'text', text: `Result: ${a} ${operation} ${b} = ${result}` }],
      };
    }

    default:
      return {
        content: [{ type: 'text', text: `Unknown tool: ${name}` }],
        isError: true,
      };
  }
});

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Custom MCP server running on stdio');
}

main().catch(console.error);
