DAGS_TO_IGNORE = (
    "airflow_clear_missing_dags", 
    "airflow_log_clean_up", 
    "airflow_metastore_clean_up",
)

DAG_EXPECTED_TASKS = {}
DAG_EXPECTED_TASKS["iceberg_optimize"] = set({"optimize_iceberg_table"})
DAG_EXPECTED_TASKS["iceberg_vacuum"] = set({"expire_iceberg_snapshots"})
DAG_EXPECTED_TASKS["job_listing"] = set({
    'get_job_listing',
    'get_job_descriptions_from_listing',
    'get_skills_from_job_description',
    'start_emr_cluster',
    'upsert_dbt_conn',
    'terminate_emr_cluster',
    'job_listing_transformation.dim__date_run',
    'job_listing_transformation.brz__job_skills_run',
    'job_listing_transformation.brz__job_listing_run',
    'job_listing_transformation.brz__job_description_run',
    'job_listing_transformation.dim__extraction_date_run',
    'job_listing_transformation.dim__ad_creation_date_run',
    'job_listing_transformation.slvr__job_skills_run',
    'job_listing_transformation.slvr__job_listing_run',
    'job_listing_transformation.slvr__job_description_run',
    'job_listing_transformation.fct__job_listing_run',
    'job_listing_transformation.dim__skill_run',
    'job_listing_transformation.brdg__job_skill_run',
    'job_listing_transformation.dim__location_run',
    'job_listing_transformation.dim__contract_type_run',
    'job_listing_transformation.dim__job_description_run',
    'job_listing_transformation.dim__company_run',
    'job_listing_transformation.dim__category_run',
    'job_listing_transformation.job_listing_test',
})

DAG_TASKS_EXPECTED_DEPENDENCIES = {}
DAG_TASKS_EXPECTED_DEPENDENCIES['iceberg_optimize'] = {}
DAG_TASKS_EXPECTED_DEPENDENCIES['iceberg_vacuum'] = {}
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing'] = {}

DAG_TASKS_EXPECTED_DEPENDENCIES['iceberg_optimize']['optimize_iceberg_table'] = {}
DAG_TASKS_EXPECTED_DEPENDENCIES['iceberg_optimize']['optimize_iceberg_table']['upstream'] = set()
DAG_TASKS_EXPECTED_DEPENDENCIES['iceberg_optimize']['optimize_iceberg_table']['downstream'] = set()

DAG_TASKS_EXPECTED_DEPENDENCIES['iceberg_vacuum']['expire_iceberg_snapshots'] = {}
DAG_TASKS_EXPECTED_DEPENDENCIES['iceberg_vacuum']['expire_iceberg_snapshots']['upstream'] = set()
DAG_TASKS_EXPECTED_DEPENDENCIES['iceberg_vacuum']['expire_iceberg_snapshots']['downstream'] = set()

DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['get_job_listing'] = {}
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['get_job_listing']['upstream'] = set()
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['get_job_listing']['downstream'] = set({'get_job_descriptions_from_listing'})

DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['get_job_descriptions_from_listing'] = {}
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['get_job_descriptions_from_listing']['upstream'] = set({'get_job_listing'})
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['get_job_descriptions_from_listing']['downstream'] = set({'get_skills_from_job_description'})

DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['get_skills_from_job_description'] = {}
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['get_skills_from_job_description']['upstream'] = set({'get_job_descriptions_from_listing'})
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['get_skills_from_job_description']['downstream'] = set({'job_listing_transformation.dim__date_run',
                                                                                              'job_listing_transformation.brz__job_skills_run',
                                                                                              'job_listing_transformation.brz__job_listing_run',
                                                                                              'job_listing_transformation.brz__job_description_run'})

DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['start_emr_cluster'] = {}
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['start_emr_cluster']['upstream'] = set()
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['start_emr_cluster']['downstream'] = set({'upsert_dbt_conn', 'terminate_emr_cluster'})

DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['upsert_dbt_conn'] = {}
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['upsert_dbt_conn']['upstream'] = set({'start_emr_cluster'})
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['upsert_dbt_conn']['downstream'] = set({'job_listing_transformation.dim__date_run',
                                                                              'job_listing_transformation.brz__job_skills_run',
                                                                              'job_listing_transformation.brz__job_listing_run',
                                                                              'job_listing_transformation.brz__job_description_run'})


DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.dim__date_run'] = {}
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.dim__date_run']['upstream'] = set({'get_skills_from_job_description',
                                                                                                     'upsert_dbt_conn'})
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.dim__date_run']['downstream'] = set({'job_listing_transformation.dim__extraction_date_run',
                                                                                                       'job_listing_transformation.dim__ad_creation_date_run'})

DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.brz__job_skills_run'] = {}
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.brz__job_skills_run']['upstream'] = set({'get_skills_from_job_description',
                                                                                                            'upsert_dbt_conn'})
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.brz__job_skills_run']['downstream'] = set({'job_listing_transformation.slvr__job_skills_run'})


DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.brz__job_listing_run'] = {}
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.brz__job_listing_run']['upstream'] = set({'get_skills_from_job_description',
                                                                                                            'upsert_dbt_conn'})
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.brz__job_listing_run']['downstream'] = set({'job_listing_transformation.slvr__job_listing_run'})


DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.brz__job_description_run'] = {}
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.brz__job_description_run']['upstream'] = set({'get_skills_from_job_description',
                                                                                                                'upsert_dbt_conn'})
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.brz__job_description_run']['downstream'] = set({'job_listing_transformation.slvr__job_description_run'})


DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.dim__extraction_date_run'] = {}
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.dim__extraction_date_run']['upstream'] = set({'job_listing_transformation.dim__date_run'})
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.dim__extraction_date_run']['downstream'] = set({'job_listing_transformation.fct__job_listing_run'})

DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.dim__ad_creation_date_run'] = {}
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.dim__ad_creation_date_run']['upstream'] = set({'job_listing_transformation.dim__date_run'})
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.dim__ad_creation_date_run']['downstream'] = set({'job_listing_transformation.fct__job_listing_run'})

DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.slvr__job_skills_run'] = {}
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.slvr__job_skills_run']['upstream'] = set({'job_listing_transformation.brz__job_skills_run'})
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.slvr__job_skills_run']['downstream'] = set({'job_listing_transformation.dim__skill_run',
                                                                                                              'job_listing_transformation.brdg__job_skill_run'})

DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.slvr__job_listing_run'] = {}
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.slvr__job_listing_run']['upstream'] = set({'job_listing_transformation.brz__job_listing_run'})
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.slvr__job_listing_run']['downstream'] = set({'job_listing_transformation.fct__job_listing_run',
                                                                                                              'job_listing_transformation.dim__location_run',
                                                                                                              'job_listing_transformation.dim__contract_type_run',
                                                                                                              'job_listing_transformation.dim__job_description_run',
                                                                                                              'job_listing_transformation.dim__company_run',
                                                                                                              'job_listing_transformation.dim__category_run'})

DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.slvr__job_description_run'] = {}
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.slvr__job_description_run']['upstream'] = set({'job_listing_transformation.brz__job_description_run'})
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.slvr__job_description_run']['downstream'] = set({'job_listing_transformation.dim__job_description_run'})

DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.fct__job_listing_run'] = {}
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.fct__job_listing_run']['upstream'] = set({'job_listing_transformation.dim__extraction_date_run',
                                                                                                            'job_listing_transformation.dim__ad_creation_date_run',
                                                                                                            'job_listing_transformation.slvr__job_listing_run'})
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.fct__job_listing_run']['downstream'] = set({'job_listing_transformation.job_listing_test'})

DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.dim__skill_run'] = {}
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.dim__skill_run']['upstream'] = set({'job_listing_transformation.slvr__job_skills_run'})
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.dim__skill_run']['downstream'] = set({'job_listing_transformation.job_listing_test'})

DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.brdg__job_skill_run'] = {}
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.brdg__job_skill_run']['upstream'] = set({'job_listing_transformation.slvr__job_skills_run'})
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.brdg__job_skill_run']['downstream'] = set({'job_listing_transformation.job_listing_test'})

DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.dim__location_run'] = {}
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.dim__location_run']['upstream'] = set({'job_listing_transformation.slvr__job_listing_run'})
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.dim__location_run']['downstream'] = set({'job_listing_transformation.job_listing_test'})

DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.dim__contract_type_run'] = {}
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.dim__contract_type_run']['upstream'] = set({'job_listing_transformation.slvr__job_listing_run'})
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.dim__contract_type_run']['downstream'] = set({'job_listing_transformation.job_listing_test'})

DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.dim__job_description_run'] = {}
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.dim__job_description_run']['upstream'] = set({'job_listing_transformation.slvr__job_listing_run',
                                                                                                                'job_listing_transformation.slvr__job_description_run'})
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.dim__job_description_run']['downstream'] = set({'job_listing_transformation.job_listing_test'})


DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.dim__company_run'] = {}
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.dim__company_run']['upstream'] = set({'job_listing_transformation.slvr__job_listing_run'})
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.dim__company_run']['downstream'] = set({'job_listing_transformation.job_listing_test'})

DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.dim__category_run'] = {}
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.dim__category_run']['upstream'] = set({'job_listing_transformation.slvr__job_listing_run'})
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.dim__category_run']['downstream'] = set({'job_listing_transformation.job_listing_test'})

DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.job_listing_test'] = {}
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.job_listing_test']['upstream'] = set({'job_listing_transformation.fct__job_listing_run',
                                                                                                        'job_listing_transformation.dim__skill_run',
                                                                                                        'job_listing_transformation.brdg__job_skill_run',
                                                                                                        'job_listing_transformation.dim__location_run',
                                                                                                        'job_listing_transformation.dim__contract_type_run',
                                                                                                        'job_listing_transformation.dim__job_description_run',
                                                                                                        'job_listing_transformation.dim__company_run',
                                                                                                        'job_listing_transformation.dim__category_run'})
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['job_listing_transformation.job_listing_test']['downstream'] = set({'terminate_emr_cluster'})

DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['terminate_emr_cluster'] = {}
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['terminate_emr_cluster']['upstream'] = set({'job_listing_transformation.job_listing_test',
                                                                                  'start_emr_cluster'})
DAG_TASKS_EXPECTED_DEPENDENCIES['job_listing']['terminate_emr_cluster']['downstream'] = set()