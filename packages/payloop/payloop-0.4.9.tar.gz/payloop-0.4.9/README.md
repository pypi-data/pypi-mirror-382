# Welcome to Payloop!

Payloop is a new infrastructure platform that helps AI companies monetize agents based on business outcomes, like leads generated or tickets resolved, rather than usage or seat-based pricing. As agents begin automating workflows across sales, support, and operations, teams need clearer pricing strategies and better visibility into what it actually costs to deliver results.

Payloop gives AI-native companies the tools to define outcomes, track margins per action, and automate billing when those outcomes are met - ultimately helping teams price more confidently and scale more efficiently.

[https://trypayloop.com/](https://trypayloop.com)

# Installation

    pip install payloop

# Usage

### OpenAI

    from openai import OpenAI
    from payloop import Payloop

    client = OpenAI(...)
    payloop = Payloop(api_key="[your Payloop API key]").openai.register(client)

### Anthropic

    import anthropic
    from payloop import Payloop

    client = anthropic.Anthropic(...)
    payloop = Payloop(api_key="[your Payloop API key]").anthropic.register(client)

### Google (GenAI)

    from google import genai
    from payloop import Payloop

    client = genai.Client(...)
    payloop = Payloop(api_key="[your Payloop API key]").google.register(client)

### LangChain (ChatBedrock)

    from langchain_aws import ChatBedrock
    from payloop import Payloop

    client = ChatBedrock(...)
    payloop = Payloop(api_key="[your Payloop API key]".langchain.register(
        chatbedrock=client
    )

### LangChain (ChatGoogleGenerativeAI)

    from langchain_google_genai import ChatGoogleGenerativeAI
    from payloop import Payloop

    client = ChatGoogleGenerativeAI(...)
    payloop = Payloop(api_key="[your Payloop API key]".langchain.register(
        chatgooglegenai=client
    )

### LangChain (ChatOpenAI)

    from langchain_openai import ChatOpenAI
    from payloop import Payloop

    client = ChatOpenAI(...)
    payloop = Payloop(api_key="[your Payloop API key]".langchain.register(
        chatopenai=client
    )

### LangChain (ChatVertexAI)

    from lanchain_google_vertexai import ChatVertexAI
    from payloop import Payloop

    client = ChatVertexAI(...)
    payloop = Payloop(api_key="[your Payloop API key]".langchain.register(
        chatvertexai=client
    )

### PydanticAI

    from payloop import Payloop
    from pydantic_ai.models.openai import OpenAIModel

    client = OpenAIModel(...)
    payloop = Payloop(api_key="[your Payloop API key]").pydantic_ai.register(client)

After you have instantiated your LLM client and registered it with Payloop all you
need to do is use the instantiated LLM object as you normally would.

# Transactions

Each call you make to any LLM client that is registered with Payloop will tag your conversation with a transaction ID. As long as the Payloop object you instantiated remains in scope, all LLM calls will be tagged with the same transaction ID.

You might use this in the case you have a single agent that first calls OpenAI, then Anthropic, then Gemini and you want to let Payloop know that all of these operations are associated with a single agent.

If you want to start a new transaction at any time you can either reinstantiate the Payloop object or execute the following call on an instantiated Payloop instance:

    payloop.new_transaction()

# Attribution

Payloop can provide usage and cost breakdowns based on the customers that are using your product. To create attribution, do the following:

    from openai import OpenAI
    from payloop import Payloop

    client = OpenAI(api_key="...")
    payloop = Payloop(api_key="[your Payloop API key]").openai.register(client)

    ...

    payloop.attribution(
        parent_id="123",
        parent_name="Customer A",
        subsidiary_id="456",
        subsidiary_name="Customer Subsidiary B",
    )

    ...

To track attribution to a parent, a parent_id must be provided. To track attribution to a subsidiary, a parent_id and subsidiary_id must be provided. We strongly encourage you to also provide names as they will be used in the portal for display. Note, providing a subsidiary is not required.

To change attribution, you do not need to instantiate a new Payloop object. It may be incorrect to do so if you want to preserve the transaction but attribute the next call to a different parent / subsidiary combination.

# Environment Variables

- `PAYLOOP_API_KEY`: Your Payloop API key (alternative to passing it to constructor)

# Supported Functionality

Payloop supports all synchronous, asynchronous and streaming implementations.
