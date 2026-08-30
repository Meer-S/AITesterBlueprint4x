{
  "name": "02_FetchJIRACreateTCAIAgent_Local_LLM_ollama",
  "nodes": [
    {
      "parameters": {
        "options": {
          "systemMessage": "You have take the JIRA id and fetch from the JIRA Tool the issue with id and create the Test Plan for it. "
        }
      },
      "type": "@n8n/n8n-nodes-langchain.agent",
      "typeVersion": 3,
      "position": [
        -528,
        -288
      ],
      "id": "becf14f4-653f-4c40-a0fa-08d720c97e1d",
      "name": "AI Agent"
    },
    {
      "parameters": {
        "model": "openai/gpt-oss-120b",
        "options": {}
      },
      "type": "@n8n/n8n-nodes-langchain.lmChatGroq",
      "typeVersion": 1,
      "position": [
        -816,
        48
      ],
      "id": "7ef2bd3f-a863-4485-a090-b74ab4d4b66d",
      "name": "Groq Chat Model",
      "credentials": {
        "groqApi": {
          "id": "9E2tVv6tTj6um38g",
          "name": "Groq n8n account"
        }
      },
      "disabled": true
    },
    {
      "parameters": {
        "model": "llama3.2:3b",
        "options": {}
      },
      "type": "@n8n/n8n-nodes-langchain.lmChatOllama",
      "typeVersion": 1,
      "position": [
        -720,
        -80
      ],
      "id": "dc58bdac-81ea-4329-9d65-ccd3515f7b11",
      "name": "Ollama Chat Model",
      "credentials": {
        "ollamaApi": {
          "id": "PrcOyxk3mRTJLfNK",
          "name": "Ollama account 5"
        }
      }
    },
    {
      "parameters": {
        "content": "# JIRA Helpul AI Agent\n",
        "height": 176,
        "width": 368
      },
      "type": "n8n-nodes-base.stickyNote",
      "position": [
        -1344,
        -400
      ],
      "typeVersion": 1,
      "id": "a842e7ac-aee3-49f8-a8da-3c40318ef2f9",
      "name": "Sticky Note"
    },
    {
      "parameters": {
        "options": {}
      },
      "type": "@n8n/n8n-nodes-langchain.chatTrigger",
      "typeVersion": 1.4,
      "position": [
        -768,
        -304
      ],
      "id": "bff50153-3b89-47b8-93b5-da934de7bc6e",
      "name": "When chat message received",
      "webhookId": "98e02c29-f86b-4e70-aebf-140ea9d19c29"
    },
    {
      "parameters": {
        "operation": "get",
        "issueKey": "={{ /*n8n-auto-generated-fromAI-override*/ $fromAI('Issue_Key', ``, 'string') }}",
        "additionalFields": {}
      },
      "type": "n8n-nodes-base.jiraTool",
      "typeVersion": 1,
      "position": [
        -224,
        -128
      ],
      "id": "6decc0ed-668e-4b35-8981-1fc982088a63",
      "name": "Get an issue in Jira Software",
      "credentials": {
        "jiraSoftwareCloudApi": {
          "id": "L77nyfUEqMEoGHWq",
          "name": "Jira SW Cloud account"
        }
      }
    }
  ],
  "pinData": {},
  "connections": {
    "Groq Chat Model": {
      "ai_languageModel": [
        []
      ]
    },
    "Ollama Chat Model": {
      "ai_languageModel": [
        [
          {
            "node": "AI Agent",
            "type": "ai_languageModel",
            "index": 0
          }
        ]
      ]
    },
    "When chat message received": {
      "main": [
        [
          {
            "node": "AI Agent",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Get an issue in Jira Software": {
      "ai_tool": [
        [
          {
            "node": "AI Agent",
            "type": "ai_tool",
            "index": 0
          }
        ]
      ]
    }
  },
  "active": false,
  "settings": {
    "executionOrder": "v1"
  },
  "versionId": "ea20bda7-5a74-4533-9d73-9b2c792b1086",
  "meta": {
    "templateCredsSetupCompleted": true,
    "instanceId": "c5b7d69aef09d65f6d843dbeb419620198dba9448e9bb3bd16f598faf54bf9f9"
  },
  "id": "dwu95UHMJObXWRE6",
  "tags": []
}