import json
import random


def run_trial(items, chance_for_item):
    drops = {}
    kills = 0
    total_drops = 0
    while len(drops) < len(items):
        kills += 1
        if random.random() < chance_for_item:
            total_drops += 1
            drop = random.choice(items)
            drops[drop] = drops.get(drop, 0) + 1
    return {
        'kills': kills,
        'total_drops': total_drops,
        'drops': drops
    }


def main():
    items = [x for x in range(28)]
    chance_for_item = (1 / 14.57) * 3
    trials = 10_000
    results = []
    kills = 0
    total_drops = 0
    for _ in range(trials):
        result = run_trial(items, chance_for_item)
        results.append(result)
        kills += result['kills']
        total_drops += result['total_drops']

    # print out totals and averages
    print('kills: ' + str(kills))
    print('total drops: ' + str(total_drops))
    print('average kills: ' + str(kills / trials))
    print('average drops: ' + str(total_drops / trials))

    # save results
    # with open('results.json', 'w') as f:
    #     json.dump(results, f, indent=4)

    output = []
    for result in results:
        output_line = []
        output_line.append(result['kills'])
        output_line.append(result['total_drops'])
        for item_id in items:
            output_line.append(result['drops'].get(item_id, 0))
        output.append(output_line)
    with open('results.csv', 'w') as f:
        # write header
        f.write('kills,total_drops,' + ','.join(str(x) for x in items) + '\n')
        for line in output:
            f.write(','.join([str(x) for x in line]) + '\n')


if __name__ == '__main__':
    main()
