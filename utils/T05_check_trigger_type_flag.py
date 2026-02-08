tirgger_pool = ["fork",
                "issue_comment",
                "issues",
                "pull_request_comment",
                "watch",
                "discussion",
                "discussion_comment",
                "pull_request",
                "pull_request_target",
                "repository_dispatch"
]

def check_triiger_type(trigger_events):
    # 0代表有问题，1代表无问题
    ret = 1

    # 无触发器，返回空列表
    if trigger_events is None:
        ret = 1
        return ret

    if isinstance(trigger_events, str):
        if trigger_events in tirgger_pool:
            ret = 0
        else:
            ret = 1
        return ret
    elif isinstance(trigger_events, list):
        for evt in trigger_events:
            if evt in tirgger_pool:
                ret = 0
                break
        return ret
    elif isinstance(trigger_events, dict):
        for evt in trigger_events:
            if evt in tirgger_pool:
                ret = 0
                break
        return ret
    else:
        ret = 0
    return ret