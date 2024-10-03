# utilities

## aws_route53_record_sets.py

Use this script to generate a list of DNS record sets from all the Hosted Zones in AWS route53 and store it in a Excel file.

### prerequisites
You can install these packages using pip, the Python package manager. Open your terminal or command prompt and run the following commands:

```shell
pip install boto3
pip install pandas
```

### Exporting or Sourcing AWS credentials

Make sure to follow the guidelines in the document below to ensure credentials as properly sourced to get the desired result

- [Exporting AWS credentials](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html)

