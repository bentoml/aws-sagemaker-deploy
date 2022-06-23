## Sagemaker Requirements

how sagemaker runs its docker images.

1. sagemaker overides the default CMD command with service and
calls docker image as `docker run <image> serve`. In our docker container the
`serve` script is what call `bentoml serve`

2. expose port 8080

3. defines 2 endpoints 
    /invocation - this is the endpoint into which the request comes in 
    / ping - sagemaker checks this to ensure the container is running

more details - [Use Your Own Inference Code with Hosting Services - Amazon SageMaker](https://docs.aws.amazon.com/sagemaker/latest/dg/your-algorithms-inference-code.html)

## Sagemaker_service

custom bentoml service that loads the bentoml service present locally. It loads a middleware which redirects the traffic comming from `/ping` to `/livez` in the bentoml service and `/invocation` to the curresponding bentoml path based on the header `AWS_CUSTOM_ENDPOINT_HEADER = "X-Amzn-SageMaker-Custom-Attributes"`.


## Running locally

1. build with bentoctl - `bentoctl build <bento_tag> --debug --dry-run`
2. docker run with the docker tag from the output of the previous step. `docker run -p 8080:8080 <docker_tag> serve`.
