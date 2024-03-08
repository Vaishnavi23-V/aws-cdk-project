# Host a web app in AWS with custom domain

1. Register a custom domain in route53 console.
2. Give npm run build in the frontend folder, dist folder gets generated which is the thing u need to deploy
3. Create a s3 bucket with the custom domain name and make it public , enable static web hosting.
4. Create another bucket with subdomain, with static web hosting enabled.
5. Upload the files in dist folder to root bucket.
6. Create a ssl certificate in certificate manager for your custom domain in us-east-1 and create a record for it in route 53 region.
7. Create a cloudfront distribution with the s3 bucket as origin , One bucket policy will get generated when the distribution get deployed, copy it and paste it in the s3 bucket policy.
8. Go to route 53, and click on create record. In that choose, A type. Click on alias to cloundfront distribution and select the created distribution
9. You will be able to access the custom domain.
