![Zen Bezos](http://i.imgur.com/6mdNXPl.png)

simpleaws
=========

An idiot-proof way to make a public AWS based service.

# Installation

1. Install it.

    ```bash
    pip install simpleaws
    ```

2. Copy settings\_template.py to settings.py and enter your keys.

3. Use your Amazon Web Services console to enable S3, CloudFront and Glacier has needed.

4. Run test\_simpleaws.py.

    ```bash
    python test_simplaws.py
    ```

# Usage

Connect to S3!

```python
simpleaws.set_keys(settings.AWS_ACCESS_KEY, settings.AWS_SECRET_ACCESS_KEY)
simpleaws.connect()
```

Create a bucket!

```python
simpleaws.create_bucket(bucketname)
```

Create a user!

```python
simpleaws.create_user(username)
```

Move a bucket to CloudFront!

```python
simpleaws.move_bucket_to_cloudfront(bucketname)
```

Backup a bucket!

```python
simpleaws.backup_bucket(bucketname)
```

Vanquish your foes!

```python
simpleaws.vanquish_foes(vanquish)
```

Just kidding.
