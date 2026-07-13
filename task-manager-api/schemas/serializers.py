def task_to_dict(task, include_overdue=False, include_relations=False):
    data = {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "user_id": task.user_id,
        "category_id": task.category_id,
        "created_at": str(task.created_at),
        "updated_at": str(task.updated_at),
        "due_date": str(task.due_date) if task.due_date else None,
        "tags": task.tags.split(",") if task.tags else [],
    }
    if include_overdue:
        data["overdue"] = task.is_overdue()
    if include_relations:
        data["user_name"] = task.user.name if task.user else None
        data["category_name"] = task.category.name if task.category else None
    return data


def user_task_to_dict(task):
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "created_at": str(task.created_at),
        "due_date": str(task.due_date) if task.due_date else None,
        "overdue": task.is_overdue(),
    }


def user_to_dict(user, include_tasks=False, include_task_count=False):
    data = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "active": user.active,
        "created_at": str(user.created_at),
    }
    if include_task_count:
        data["task_count"] = len(user.tasks)
    if include_tasks:
        data["tasks"] = [task_to_dict(task) for task in user.tasks]
    return data


def category_to_dict(category, task_count=None):
    data = {
        "id": category.id,
        "name": category.name,
        "description": category.description,
        "color": category.color,
        "created_at": str(category.created_at),
    }
    if task_count is not None:
        data["task_count"] = task_count
    return data
