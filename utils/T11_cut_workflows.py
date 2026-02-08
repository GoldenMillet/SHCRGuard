def get_cuted_workflows(workflow, job_name, threshold):
    ret = workflow
    if len(str(ret)) >= threshold:
        temp = ret
        ret = {}
        ret['jobs'] = {}
        needs = []
        if temp['jobs'][job_name].get('needs') is not None:
            if isinstance(temp['jobs'][job_name]['needs'], str):
                needs = [temp['jobs'][job_name]['needs']]
            elif isinstance(temp['jobs'][job_name]['needs'], list):
                needs = temp['jobs'][job_name]['needs']
            else:
                """do nothing"""

            ret['jobs'][job_name] = temp['jobs'][job_name]
            for job_name_needs in needs:
                if temp['jobs'].get(job_name_needs) is not None:
                    ret['jobs'][job_name_needs] = temp['jobs'][job_name_needs]
        else:
            ret['jobs'] = workflow['jobs'][job_name]

        if len(str(ret)) >= threshold:
            temp = ret['jobs'][job_name]
            ret['jobs'][job_name] = {}
            ret['jobs'][job_name] = temp

            if len(str(ret)) >= threshold:
                platform = ret['jobs'][job_name].get('runs_on') or ret['jobs'][job_name].get('runs-on')
                ret = platform

    return ret
