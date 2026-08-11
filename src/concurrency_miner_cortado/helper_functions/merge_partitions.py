def merge_partitions(activity_a, activity_b, partitions):
    partition_a = next(p for p in partitions if activity_a in p)
    partition_b = next(p for p in partitions if activity_b in p)

    if not partition_a is partition_b:
        partitions.remove(partition_a)
        partitions.remove(partition_b)
        partition_a.update(partition_b)
        partitions.append(partition_a)
