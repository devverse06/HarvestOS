import React, { useEffect, useState } from 'react';
import { cancelOrder, createOrder, getBuyers, getInventory, getOrders } from '../services/api';

export default function Orders() {
    const [orders, setOrders] = useState<any[]>([]);
    const [buyers, setBuyers] = useState<any[]>([]);
    const [inventory, setInventory] = useState<any[]>([]);
    const [buyerId, setBuyerId] = useState('');
    const [batchId, setBatchId] = useState('');
    const [quantity, setQuantity] = useState('');
    const [error, setError] = useState('');

    const load = async () => {
        const [orderData, buyerData, inventoryData] = await Promise.all([getOrders(), getBuyers(), getInventory()]);
        setOrders(orderData);
        setBuyers(buyerData);
        setInventory(inventoryData.filter((batch) => batch.available_tons > 0));
    };

    useEffect(() => { load().catch((err) => setError(err.message)); }, []);

    const submit = async (event: React.FormEvent) => {
        event.preventDefault();
        setError('');
        try {
            await createOrder({
                id: `ORD-${Date.now()}`,
                buyer_id: buyerId,
                lines: [{ inventory_batch_id: batchId, quantity_tons: Number(quantity) }],
            });
            setBuyerId('');
            setBatchId('');
            setQuantity('');
            await load();
        } catch (err: any) {
            setError(err.message);
        }
    };

    const cancel = async (id: string) => {
        try {
            await cancelOrder(id);
            await load();
        } catch (err: any) {
            setError(err.message);
        }
    };

    return (
        <div className="flex-1 overflow-auto p-6 absolute inset-0 bg-[#F8FAFC]">
            <div className="mb-6"><h1 className="text-2xl font-semibold text-slate-900">Orders</h1><p className="text-sm text-slate-500 mt-1">Reserve available inventory for customer orders.</p></div>
            {error && <p className="mb-4 text-sm text-red-600">{error}</p>}
            <form onSubmit={submit} className="bg-white border border-slate-200 rounded-lg p-5 mb-6 grid grid-cols-1 md:grid-cols-4 gap-3">
                <select required value={buyerId} onChange={(event) => setBuyerId(event.target.value)} className="border border-slate-300 rounded-md px-3 py-2 text-sm"><option value="">Select buyer</option>{buyers.map((buyer) => <option key={buyer.id} value={buyer.id}>{buyer.company_name}</option>)}</select>
                <select required value={batchId} onChange={(event) => setBatchId(event.target.value)} className="border border-slate-300 rounded-md px-3 py-2 text-sm"><option value="">Select inventory batch</option>{inventory.map((batch) => <option key={batch.id} value={batch.id}>{batch.id} ({batch.available_tons.toFixed(2)} t available)</option>)}</select>
                <input required min="0.01" step="0.01" type="number" value={quantity} onChange={(event) => setQuantity(event.target.value)} placeholder="Quantity (tons)" className="border border-slate-300 rounded-md px-3 py-2 text-sm" />
                <button type="submit" className="bg-slate-900 text-white rounded-md px-4 py-2 text-sm font-medium">Reserve order</button>
            </form>
            <div className="bg-white border border-slate-200 rounded-lg overflow-hidden"><table className="w-full text-sm text-left"><thead className="bg-slate-50 text-xs uppercase text-slate-500"><tr><th className="p-4">Order</th><th className="p-4">Buyer</th><th className="p-4">Lines</th><th className="p-4">Status</th><th className="p-4">Action</th></tr></thead><tbody>{orders.map((order) => <tr key={order.id} className="border-t border-slate-100"><td className="p-4 font-medium">{order.id}</td><td className="p-4">{order.buyer_id}</td><td className="p-4">{order.lines.reduce((sum: number, line: any) => sum + line.quantity_tons, 0).toFixed(2)} t</td><td className="p-4">{order.status}</td><td className="p-4">{order.status === 'Reserved' && <button onClick={() => cancel(order.id)} className="text-red-600 hover:underline">Cancel</button>}</td></tr>)}</tbody></table></div>
        </div>
    );
}
