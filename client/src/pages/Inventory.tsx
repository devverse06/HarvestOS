import React, { useEffect, useState } from 'react';
import { getHarvestLots, getInventory, getWarehouses } from '../services/api';

export default function Inventory() {
    const [inventory, setInventory] = useState<any[]>([]);
    const [warehouses, setWarehouses] = useState<any[]>([]);
    const [lots, setLots] = useState<any[]>([]);
    const [error, setError] = useState('');

    useEffect(() => {
        Promise.all([getInventory(), getWarehouses(), getHarvestLots()])
            .then(([inventoryData, warehouseData, lotData]) => {
                setInventory(inventoryData);
                setWarehouses(warehouseData);
                setLots(lotData);
            })
            .catch((err) => setError(err.message));
    }, []);

    const warehouseName = (id: string) => warehouses.find((warehouse) => warehouse.id === id)?.name || id;
    const lotLabel = (id: string) => lots.find((lot) => lot.id === id)?.quality_grade || id;

    return (
        <div className="flex-1 overflow-auto p-6 absolute inset-0 bg-[#F8FAFC]">
            <div className="mb-6">
                <h1 className="text-2xl font-semibold text-slate-900">Inventory</h1>
                <p className="text-sm text-slate-500 mt-1">Available and reserved stock by harvest lot and warehouse.</p>
            </div>
            {error && <p className="mb-4 text-sm text-red-600">{error}</p>}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-white border border-slate-200 rounded-lg p-4"><p className="text-xs text-slate-500">Batches</p><p className="text-2xl font-semibold">{inventory.length}</p></div>
                <div className="bg-white border border-slate-200 rounded-lg p-4"><p className="text-xs text-slate-500">Available tons</p><p className="text-2xl font-semibold">{inventory.reduce((sum, batch) => sum + batch.available_tons, 0).toFixed(2)}</p></div>
                <div className="bg-white border border-slate-200 rounded-lg p-4"><p className="text-xs text-slate-500">Reserved tons</p><p className="text-2xl font-semibold">{inventory.reduce((sum, batch) => sum + batch.reserved_tons, 0).toFixed(2)}</p></div>
            </div>
            <div className="bg-white border border-slate-200 rounded-lg overflow-hidden">
                <table className="w-full text-sm text-left">
                    <thead className="bg-slate-50 text-xs uppercase text-slate-500"><tr><th className="p-4">Batch</th><th className="p-4">Lot</th><th className="p-4">Warehouse</th><th className="p-4">Available</th><th className="p-4">Reserved</th><th className="p-4">Status</th></tr></thead>
                    <tbody>{inventory.map((batch) => <tr key={batch.id} className="border-t border-slate-100"><td className="p-4 font-medium">{batch.id}</td><td className="p-4">{batch.lot_id} ({lotLabel(batch.lot_id)})</td><td className="p-4">{warehouseName(batch.warehouse_id)}</td><td className="p-4">{batch.available_tons.toFixed(2)} t</td><td className="p-4">{batch.reserved_tons.toFixed(2)} t</td><td className="p-4">{batch.status}</td></tr>)}</tbody>
                </table>
            </div>
        </div>
    );
}
