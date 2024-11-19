import * as devalue from 'devalue';
import { decompress } from 'compress-json';
import fs from 'fs/promises';

const INTERVAL = 30000; // Set refresh interval (e.g., 30 seconds)
const GROUP = "30001"; // Region to filter for

const fetchData = async () => {
    try {
        // Fetch the first dataset
        const apiResp = await fetch('https://tldb.info/auction-house/__data.json').then((r) => r.json());
        const apiData1 = devalue.unflatten(apiResp.nodes.find((e) => e?.type === 'data').data);

        const items = decompress(apiData1.items);
        const traits = apiData1.traits;

        // Fetch the second dataset
        const apiData2 = await fetch('https://tldb.info/api/ah/prices').then((r) => r.json());
        let { list, total, regions } = apiData2;

        // Decompress and filter for the region
        Object.keys(list).forEach((server) => {
            list[server] = decompress(JSON.parse(list[server]));
        });

        const filteredList = list[GROUP] || {};

        // Save each data component to a separate JSON file
        await Promise.all([
            fs.writeFile('items.json', JSON.stringify(items, null, 2), 'utf8'),
            fs.writeFile('traits.json', JSON.stringify(traits, null, 2), 'utf8'),
            fs.writeFile('list.json', JSON.stringify(filteredList, null, 2), 'utf8'),
            fs.writeFile('total.json', JSON.stringify(total, null, 2), 'utf8'),
            fs.writeFile('regions.json', JSON.stringify(regions, null, 2), 'utf8'),
        ]);

        console.log(`[${new Date().toISOString()}] Data refreshed and saved to files.`);
    } catch (error) {
        console.error('Error fetching or saving data:', error);
    }
};

const startAutoRefresh = () => {
    console.log('Starting auto-refresh...');
    fetchData(); // Fetch immediately on startup
    setInterval(fetchData, INTERVAL); // Fetch periodically
};

startAutoRefresh();
