# mpyl-example-simple
A simple example, demonstrating [mpyl](https://github.com/Vandebron/mpyl/). Without deployment.

## Instructions

First time use
```shell
poetry install
```

MPyL CLI help:
```shell
poetry run mp
```

Check build status:
```shell
poetry run mp build status
````
Make a random change, for example to [ApplicationOne.kt](com/example/multimodule/service/ApplicationOne.kt)

The changed module should show up as changed. After which, you can build it. 
```shell
poetry run mp build status
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
```poetry run mp build status```

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
poetry run mp build clean
```

## Dagster as runner
To use dagster as runner, do:
```shell
poetry run dagster dev -f mpyl-dagster-example.py
```
Then, in the [web interface](http://127.0.0.1:3000/), click _Launchpad_ -> _Launch run_.

## Adding custom build steps
Build steps can be defined in python code anywhere, as long as they are registered in [run.py](cicd/run.py).
Example steps are defined under [cicd/steps](cicd/steps). Information on the `Step` interface can be found in the 
[documentation](https://vandebron.github.io/mpyl/mpyl/steps.html).
