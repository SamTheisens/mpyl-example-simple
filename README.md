# mpyl-example-simple
A simple example, demonstrating mpyl. Without deployment.

## Instructions

First time use
```shell
poetry install
```

Check build status:
```shell
poetry run mpyl build status
````
Make a random change, for example to [ApplicationOne.kt](com/example/multimodule/service/ApplicationOne.kt)

The changed module should show up as changed. After which, you can build it. 
```shell
poetry run mpyl build status
poetry run build
```
Which should have the following outcome:

✅ Successful                                                                                                                                                                                                
🏗️ Build:                                                                                                                                                                                                     
gradle1                                                                                                                                                                                                      
📦 Assemble:                                                                                                                                                                                                 
gradle1                                                                                                                                                                                                      
📋 Test:                                                                                                                                                                                                     
gradle1                                                                                                                                                                                                      
🧪 1 ❌ 0 💔 0 🙈 0


The status should update to:
```poetry run mpyl build status```
[11:00:18] INFO     Discovering run plan...                                                                                                                     
           INFO     MPyL log level is set to INFO                                                                                                               
Execution plan:                                                                                                                                                 
🏗️ Build:                                                                                                                                                        
gradle1 (cached)                                                                                                                                                
📦 Assemble:                                                                                                                                                    
gradle1 (cached)                                                                                                                                                
📋 Test:                                                                                                                                                        
gradle1 (cached) 

To clean up cached artifacts, run:

```shell
poetry run mpyl build clean
```

## Dagster as runner
To use dagster as runner, do:
```shell
poetry run dagster dev -f mpyl-dagster-example.py
```
Then, in the [web interface](http://127.0.0.1:3000/), click _Launchpad_ -> _Launch run_.

