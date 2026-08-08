def merge_partitions(activity_a, activity_b, partitions):
    partition_a = next(p for p in partitions if activity_a in p)
    partition_b = next(p for p in partitions if activity_b in p)

    if not partition_a is partition_b:
        partitions.remove(partition_a)
        partitions.remove(partition_b)
        partition_a.update(partition_b)
        partitions.append(partition_a)



def add_partitions_with_no_start_or_end_to_arbitrary(partitions, start_activities, end_activities):
    changed = True
    while changed:
        changed = False
        if len(partitions) <= 1:
            continue
        i = 0
        for partition in partitions:
            has_start = False
            has_end = False
            for activity in partition:
                if activity.activity_exists_by_label(start_activities):
                    has_start = True
                if activity.activity_exists_by_label(end_activities):
                    has_end = True
            if not has_start and not has_end:
                if i == 0:
                    merge_partitions(partitions[0][0], partitions[1][0], partitions)
                if i > 0:
                    merge_partitions(partitions[i][0], partitions[0][0], partitions)
                changed = True
            i += 1
    return partitions
