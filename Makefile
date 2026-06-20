.PHONY: ingest spark-staging spark-prod bq-load dbt-run dbt-test pipeline

ingest:
	poetry run python ingestion/sncf_api.py

spark-staging:
	docker run --env-file .env -v $(PWD):/app transport-spark \
		spark-submit \
		--py-files /app/spark/utils/spark_session.py \
		/app/spark/jobs/raw_to_staging.py

spark-prod:
	docker run --env-file .env -v $(PWD):/app transport-spark \
		spark-submit \
		--py-files /app/spark/utils/spark_session.py \
		/app/spark/jobs/staging_to_prod.py

bq-load:
	bq load --replace \
		--source_format=PARQUET \
		transport-data-platform-2026:transport_data.departures_prod \
		gs://transport-data-platform-paskal/prod/departures/*.parquet

dbt-run:
	cd transport_dbt && poetry run dbt run

dbt-test:
	cd transport_dbt && poetry run dbt test

pipeline:
	make ingest
	make spark-staging
	make spark-prod
	make bq-load
	make dbt-run
	make dbt-test