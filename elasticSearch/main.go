package main

import (
	"bytes"
	"encoding/json"
	"log"
	"net/http"
	"os"
	"time"

	"context"

	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go/aws/credentials"
	v4 "github.com/aws/aws-sdk-go/aws/signer/v4"
)

func main() {
	lambda.Start(HandleRequest)
}

type EventDetail struct {
	EventVersion string `json:"eventVersion"`
	UserIdentity struct {
		Type           string `json:"type"`
		PrincipalID    string `json:"principalId"`
		Arn            string `json:"arn"`
		AccountID      string `json:"accountId"`
		SessionContext struct {
			Attributes struct {
				MfaAuthenticated string    `json:"mfaAuthenticated"`
				CreationDate     time.Time `json:"creationDate"`
			} `json:"attributes"`
		} `json:"sessionContext"`
	} `json:"userIdentity"`
	EventTime         time.Time `json:"eventTime"`
	EventSource       string    `json:"eventSource"`
	EventName         string    `json:"eventName"`
	AwsRegion         string    `json:"awsRegion"`
	SourceIPAddress   string    `json:"sourceIPAddress"`
	UserAgent         string    `json:"userAgent"`
	RequestParameters struct {
		BucketName string `json:"bucketName"`
	} `json:"requestParameters"`
	ResponseElements interface{} `json:"responseElements"`
	RequestID        string      `json:"requestID"`
	EventID          string      `json:"eventID"`
	EventType        string      `json:"eventType"`
}

func HandleRequest(ctx context.Context, event events.CloudWatchEvent) error {
	log.Print(event)
	domain := os.Getenv("ES_HOST")
	index := "iam-user-" + event.Time.Format("2006-01-02")
	endpoint := domain + "/" + index + "/" + "_doc" + "/"
	region := os.Getenv("ES_REGION")
	service := "es"

	b, err := json.Marshal(event)
	if err != nil {
		log.Print(err)
		return err
	}

	// json := string(b)
	// body := strings.NewReader(json)
	body := bytes.NewReader(b)

	// credentials := credentials.NewSharedCredentials("", "devops")
	credentials := credentials.NewEnvCredentials()
	signer := v4.NewSigner(credentials)
	client := &http.Client{}
	req, err := http.NewRequest(http.MethodPost, endpoint, body)
	if err != nil {
		log.Print(err)
		return err
	}

	req.Header.Add("Content-Type", "application/json")
	signer.Sign(req, body, service, region, time.Now())
	resp, err := client.Do(req)
	if err != nil {
		log.Print(err)
		return err
	}
	log.Print(resp)
	return nil
}
