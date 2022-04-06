fmt:
	# Format the file in repo
	terraform fmt ./bentoctl_sagemaker/templates/*.tf && \
		echo "Formated terraform templates"
	isort bentoctl_sagemaker tests
	black bentoctl_sagemaker tests
