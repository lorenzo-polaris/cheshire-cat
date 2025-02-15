"""Hooks to modify the Cat's flow of execution.

Here is a collection of methods to hook into the Cat execution pipeline.

"""

from cat.mad_hatter.decorators import hook


# Called before cat bootstrap
@hook(priority=0)
def before_cat_bootstrap(cat) -> None:
    """Hook into the Cat start up.

    Bootstrapping is the process of loading the plugins, the natural language objects (e.g. the LLM),
    the memories, the *Agent Manager* and the *Rabbit Hole*.

    This hook allows to intercept such process and is executed in the middle of plugins and
    natural language objects loading.

    This hook can be used to set or store variables to be propagated to subsequent loaded objects.

    Parameters
    ----------
    cat : CheshireCat
        Cheshire Cat instance.
    """
    return None


# Called after cat bootstrap
@hook(priority=0)
def after_cat_bootstrap(cat) -> None:
    """Hook into the end of the Cat start up.

    Bootstrapping is the process of loading the plugins, the natural language objects (e.g. the LLM),
    the memories, the *Agent Manager* and the *Rabbit Hole*.

    This hook allows to intercept the end of such process and is executed right after the Cat has finished loading
    its components.

    This can be used to set or store variables to be shared further in the pipeline.

    Parameters
    ----------
    cat : CheshireCat
        Cheshire Cat instance.
    """
    return None


# Called when a user message arrives.
# Useful to edit/enrich user input (e.g. translation)
@hook(priority=0)
def before_cat_reads_message(user_message_json: dict, cat) -> dict:
    """Hook the incoming user's JSON dictionary.

    Allows to edit and enrich the incoming message received from the WebSocket connection.

    For instance, this hook can be used to translate the user's message before feeding it to the Cat.
    Another use case is to add custom keys to the JSON dictionary.

    The incoming message is a JSON dictionary with keys:
        {
            "text": message content
        }

    Parameters
    ----------
    user_message_json : dict
        JSON dictionary with the message received from the chat.
    cat : CheshireCat
        Cheshire Cat instance.


    Returns
    -------
    user_message_json : dict
        Edited JSON dictionary that will be fed to the Cat.

    Notes
    -----
    For example:

        {
            "text": "Hello Cheshire Cat!",
            "custom_key": True
        }

    where "custom_key" is a newly added key to the dictionary to store any data.

    """
    return user_message_json


# Called just before the cat recalls memories.
@hook(priority=0)
def before_cat_recalls_memories(user_message: str, cat) -> tuple[int, float, int, float, int, float]:
    """Hook into semantic search in memories.

    Allows to intercept when the Cat queries the memories using the embedded user's input.

    The hook is executed just before the Cat searches for the meaningful context in both memories
    and stores it in the *Working Memory*.

    The hook return the values for maximum number (k) of items to retrieve from memory and the score threshold applied
    to the query in the vector memory (items with score under threshold are not retrieved)

    Parameters
    ----------
    user_message : str
        String with the text received from the user. This is used as a query to search into memories.
    cat : CheshireCat
     Cheshire Cat instance.

    Returns
    -------
    k_memory_type : int
        Number of relevant memories to retrieve from the vector database.
    threshold_memory_type : float
        Threshold to filter memories according their similarity score with the query.
    """
    k_episodic = 3
    threshold_episodic = 0.7
    k_declarative = 3
    threshold_declarative = 0.7
    k_procedural = 3
    threshold_procedural = 0.7
    return k_episodic, threshold_episodic, k_declarative, threshold_declarative, k_procedural, threshold_procedural


# Called just before the cat recalls memories.
@hook(priority=0)
def after_cat_recalls_memories(query: str, cat) -> None:
    """Hook after semantic search in memories.

    The hook is executed just after the Cat searches for the meaningful context in both memories
    and stores it in the *Working Memory*.

    Parameters
    ----------
    query : str
        Query used to retrieve memories.
    cat : CheshireCat
     Cheshire Cat instance.
       
    """
    return None


# What is the input to recall memories?
# Here you can do HyDE embedding, condense recent conversation or condition recall query on something else important to your AI
@hook(priority=0)
def cat_recall_query(user_message: str, cat) -> str:
    """Hook the Hypothetical Document Embedding (HyDE) search query.

    This hook allows to edit the user's message used as a query for HyDE.
    As a result, context retrieval can be conditioned enhancing such message.

    Parameters
    ----------
    user_message : str
        String with the text received from the user.
    cat : CheshireCat
        Cheshire Cat instance to exploit the Cat's methods.

    Returns
    -------
    Edited string to be used for context retrieval in memory. The returned string is further stored in the
    Working Memory at `cat.working_memory["memory_query"]`.

    Notes
    -----
    HyDE [1]_ strategy exploits the user's message to generate a hypothetical answer. This is then applied to recall
    the relevant context from the memory.

    References
    ----------
    .. [1] Gao, L., Ma, X., Lin, J., & Callan, J. (2022). Precise Zero-Shot Dense Retrieval without Relevance Labels.
       arXiv preprint arXiv:2212.10496.

    """
    # example 1: HyDE embedding
    # return cat.hypothetis_chain.run(user_message)

    # example 2: Condense recent conversation
    # TODO

    # here we just return the latest user message as is
    return user_message


# Called just after memories are recalled. They are stored in:
# - cat.working_memory["episodic_memories"]
# - cat.working_memory["declarative_memories"]
@hook(priority=0)
def after_cat_recalled_memories(memory_query_text: str, cat) -> None:
    """Hook into semantic search after the memory retrieval.

    Allows to intercept the recalled memories right after these are stored in the Working Memory.
    According to the user's input, the relevant context is saved in `cat.working_memory["episodic_memories"]`
    and `cat.working_memory["declarative_memories"]`. At this point,
    this hook is executed to edit the search query.

    Parameters
    ----------
    memory_query_text : str
        String used to query both *episodic* and *declarative* memories.
    cat : CheshireCat
        Cheshire Cat instance.
    """
    return None


# Hook called just before sending response to a client.
@hook(priority=0)
def before_cat_sends_message(message: dict, cat) -> dict:
    """Hook the outgoing Cat's message.

    Allows to edit the JSON dictionary that will be sent to the client via WebSocket connection.

    This hook can be used to edit the message sent to the user or to add keys to the dictionary.

    Parameters
    ----------
    message : dict
        JSON dictionary to be sent to the WebSocket client.
    cat : CheshireCat
        Cheshire Cat instance.

    Returns
    -------
    message : dict
        Edited JSON dictionary with the Cat's answer.

    Notes
    -----
    Default `message` is::

            {
                "error": False,
                "type": "chat",
                "content": cat_message["output"],
                "why": {
                    "input": cat_message["input"],
                    "output": cat_message["output"],
                    "intermediate_steps": cat_message["intermediate_steps"],
                    "memory": {
                        "vectors": {
                            "episodic": episodic_report,
                            "declarative": declarative_report
                        }
                    },
                },
            }

    """

    return message
