#!/bin/bash

RESOURCE_GROUP_NAME=${RESOURCE_GROUP_NAME:-"rg-autopodcaster"}
LOCATION=${LOCATION:-"swedencentral"}
SERVICEBUS_NAMESPACE_NAME=${SERVICEBUS_NAMESPACE_NAME:-"sb-autopodcaster"}

az group create --name $RESOURCE_GROUP_NAME --location $LOCATION
az servicebus namespace create --resource-group $RESOURCE_GROUP_NAME --name $SERVICEBUS_NAMESPACE_NAME --location $LOCATION

# Create queues for text, PDF, video and website
az servicebus queue create --resource-group $RESOURCE_GROUP_NAME --namespace-name $SERVICEBUS_NAMESPACE_NAME --name "note" --enable-partitioning true
az servicebus queue create --resource-group $RESOURCE_GROUP_NAME --namespace-name $SERVICEBUS_NAMESPACE_NAME --name "pdf" --enable-partitioning true
az servicebus queue create --resource-group $RESOURCE_GROUP_NAME --namespace-name $SERVICEBUS_NAMESPACE_NAME --name "word" --enable-partitioning true
az servicebus queue create --resource-group $RESOURCE_GROUP_NAME --namespace-name $SERVICEBUS_NAMESPACE_NAME --name "video" --enable-partitioning true
az servicebus queue create --resource-group $RESOURCE_GROUP_NAME --namespace-name $SERVICEBUS_NAMESPACE_NAME --name "website" --enable-partitioning true

# Get the connection string for the Service Bus namespace
SERVICEBUS_CONNECTION_STRING=$(az servicebus namespace authorization-rule keys list --resource-group $RESOURCE_GROUP_NAME --namespace-name $SERVICEBUS_NAMESPACE_NAME --name RootManageSharedAccessKey --query primaryConnectionString --output tsv)

# Create a storage account for multipart file upload with a blob container
STORAGE_ACCOUNT_NAME=${STORAGE_ACCOUNT_NAME:-"stautopodcaster"}
az storage account create --name $STORAGE_ACCOUNT_NAME --resource-group $RESOURCE_GROUP_NAME --location $LOCATION --sku Standard_LRS
az storage container create --name "uploads" --account-name $STORAGE_ACCOUNT_NAME

# Get the connection string for the storage account
STORAGE_CONNECTION_STRING=$(az storage account show-connection-string --name $STORAGE_ACCOUNT_NAME --query connectionString --output tsv)