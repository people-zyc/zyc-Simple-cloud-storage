(function (Scratch) {
  'use strict';
  const vm = Scratch.vm;

  class FileServerExtension {
    constructor() {
      this.serverUrl = 'http://127.0.0.1:5000';
      this.password = 'default_password';
    }

    getInfo() {
      return {
        id: 'zyc_file_server',
        name: 'Zyc File Server',
        color1: '#4B8BBE',
        color2: '#306998',
        blocks: [
          {
            opcode: 'setConfig',
            blockType: Scratch.BlockType.COMMAND,
            text: '设置服务器 地址[URL] 密码[PWD]',
            arguments: {
              URL: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: 'http://127.0.0.1:5000'
              },
              PWD: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: 'default_password'
              }
            }
          },
          {
            opcode: 'checkConnection',
            blockType: Scratch.BlockType.BOOLEAN,
            text: '服务器在线?',
          },
          {
            opcode: 'checkPassword',
            blockType: Scratch.BlockType.BOOLEAN,
            text: '密码正确?',
          },
          {
            opcode: 'listDirectory',
            blockType: Scratch.BlockType.REPORTER,
            text: '列出目录[PATH]',
            arguments: {
              PATH: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: ''
              }
            }
          },
          {
            opcode: 'createDirectory',
            blockType: Scratch.BlockType.COMMAND,
            text: '创建目录[PATH]',
            arguments: {
              PATH: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: 'new_folder'
              }
            }
          },
          {
            opcode: 'createFile',
            blockType: Scratch.BlockType.COMMAND,
            text: '创建文件[PATH]',
            arguments: {
              PATH: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: 'new_file.txt'
              }
            }
          },
          {
            opcode: 'writeFile',
            blockType: Scratch.BlockType.COMMAND,
            text: '写入内容到[PATH] 内容[CONTENT]',
            arguments: {
              PATH: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: 'file.txt'
              },
              CONTENT: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: 'Hello World'
              }
            }
          },
          {
            opcode: 'readFile',
            blockType: Scratch.BlockType.REPORTER,
            text: '读取[PATH]',
            arguments: {
              PATH: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: 'file.txt'
              }
            }
          },
          {
            opcode: 'deletePath',
            blockType: Scratch.BlockType.COMMAND,
            text: '删除[PATH]',
            arguments: {
              PATH: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: 'old_file.txt'
              }
            }
          }
        ]
      };
    }

    async _fetchApi(endpoint, method, params = {}) {
      const url = new URL(`${this.serverUrl}${endpoint}`);
      
      // 添加Base64编码的密码到请求参数
      params.password = btoa(this.password);

      const options = {
        method: method,
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(params)
      };

      try {
        const response = await fetch(url.toString(), options);
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(`HTTP ${response.status} - ${errorData.error}`);
        }
        return await response.json();
      } catch (error) {
        console.error(`API请求失败: ${error.message}`);
        throw error;
      }
    }

    setConfig(args) {
      this.serverUrl = args.URL.replace(/\/$/, '');
      this.password = args.PWD;
    }

    async checkConnection() {
      try {
        const response = await fetch(`${this.serverUrl}/ping`);
        return response.ok;
      } catch {
        return false;
      }
    }

    async checkPassword() {
      try {
        const testResponse = await this._fetchApi('/files', 'POST', { path: '' });
        return !!testResponse &&
               typeof testResponse.path === 'string' &&
               Array.isArray(testResponse.contents);
      } catch (error) {
        return error.message === 'HTTP 401 - Unauthorized';
      }
    }

    async listDirectory(args) {
      const response = await this._fetchApi('/files', 'POST', {
        path: args.PATH
      });
      return JSON.stringify(response.contents);
    }

    async createDirectory(args) {
      await this._fetchApi('/files', 'POST', {
        path: args.PATH
      });
    }

    async createFile(args) {
      await this._fetchApi('/files', 'POST', {
        path: args.PATH
      });
    }

    async writeFile(args) {
      await this._fetchApi('/files/content', 'PUT', {
        path: args.PATH,
        content: String(args.CONTENT)
      });
    }

    async readFile(args) {
      const response = await this._fetchApi('/files/content', 'POST', {
        path: args.PATH
      });
      return response.content;
    }

    async deletePath(args) {
      await this._fetchApi('/files', 'DELETE', {
        path: args.PATH
      });
    }
  }

  Scratch.extensions.register(new FileServerExtension());
})(Scratch);
