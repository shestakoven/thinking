import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { arbitrageApi } from '../services/api';
import { ArbitrageOpportunity, Stats } from '../types';

const ArbitrageDashboard: React.FC = () => {
    const [opportunities, setOpportunities] = useState<ArbitrageOpportunity[]>([]);
    const [loading, setLoading] = useState(true);
    const [executing, setExecuting] = useState<string | null>(null);
    const [stats, setStats] = useState<Stats>({
        totalOpportunities: 0,
        totalProfitPotential: 0,
        bestOpportunity: 0,
        averageConfidence: 0
    });

    useEffect(() => {
        fetchOpportunities();
        const interval = setInterval(fetchOpportunities, 30000); // Update every 30s
        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        calculateStats();
    }, [opportunities]);

    const fetchOpportunities = async () => {
        try {
            const data = await arbitrageApi.getOpportunities();
            setOpportunities(data);
        } catch (error) {
            console.error('Error fetching opportunities:', error);
        } finally {
            setLoading(false);
        }
    };

    const executeArbitrage = async (opportunity: ArbitrageOpportunity) => {
        setExecuting(opportunity.id);
        try {
            const response = await arbitrageApi.executeArbitrage({
                opportunity_id: opportunity.id,
                amount: 1000
            });
            
            if (response.status === 'execution_started') {
                alert('Arbitrage execution initiated!');
                // Refresh opportunities after execution
                setTimeout(() => fetchOpportunities(), 5000);
            } else {
                alert('Error executing arbitrage');
            }
        } catch (error) {
            console.error('Error executing arbitrage:', error);
            alert('Error executing arbitrage');
        } finally {
            setExecuting(null);
        }
    };

    const calculateStats = () => {
        if (opportunities.length === 0) return;

        const totalProfit = opportunities.reduce((sum, opp) => sum + opp.net_profit, 0);
        const bestOpportunity = opportunities[0]?.net_profit || 0;
        const averageConfidence = opportunities.reduce((sum, opp) => sum + opp.confidence_score, 0) / opportunities.length;

        setStats({
            totalOpportunities: opportunities.length,
            totalProfitPotential: totalProfit,
            bestOpportunity,
            averageConfidence
        });
    };

    const formatTokenAddress = (address: string) => {
        return `${address.slice(0, 8)}...${address.slice(-6)}`;
    };

    const formatPrice = (price: number) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2,
            maximumFractionDigits: 6
        }).format(price);
    };

    const formatPercentage = (value: number) => {
        return `${(value * 100).toFixed(2)}%`;
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">
                        Cross-Chain Arbitrage Platform
                    </h1>
                    <p className="text-gray-600">
                        Real-time arbitrage opportunities across multiple blockchains
                    </p>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    <div className="bg-white rounded-lg shadow p-6">
                        <h3 className="text-sm font-medium text-gray-500 mb-2">Active Opportunities</h3>
                        <p className="text-2xl font-bold text-gray-900">{stats.totalOpportunities}</p>
                    </div>
                    <div className="bg-white rounded-lg shadow p-6">
                        <h3 className="text-sm font-medium text-gray-500 mb-2">Total Profit Potential</h3>
                        <p className="text-2xl font-bold text-green-600">{formatPrice(stats.totalProfitPotential)}</p>
                    </div>
                    <div className="bg-white rounded-lg shadow p-6">
                        <h3 className="text-sm font-medium text-gray-500 mb-2">Best Opportunity</h3>
                        <p className="text-2xl font-bold text-blue-600">{formatPrice(stats.bestOpportunity)}</p>
                    </div>
                    <div className="bg-white rounded-lg shadow p-6">
                        <h3 className="text-sm font-medium text-gray-500 mb-2">Avg Confidence</h3>
                        <p className="text-2xl font-bold text-purple-600">{formatPercentage(stats.averageConfidence)}</p>
                    </div>
                </div>

                {/* Opportunities Table */}
                <div className="bg-white rounded-lg shadow">
                    <div className="px-6 py-4 border-b border-gray-200">
                        <h2 className="text-xl font-semibold text-gray-900">Arbitrage Opportunities</h2>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Token
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Source Chain
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Target Chain
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Price Difference
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Net Profit
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Confidence
                                    </th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                        Action
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {opportunities.map((opp) => (
                                    <tr key={opp.id} className="hover:bg-gray-50">
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                            {formatTokenAddress(opp.token_address)}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                                {opp.source_chain}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                                {opp.target_chain}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            {formatPercentage(opp.price_difference / opp.source_price)}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-green-600">
                                            {formatPrice(opp.net_profit)}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            {formatPercentage(opp.confidence_score)}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            <button
                                                onClick={() => executeArbitrage(opp)}
                                                disabled={opp.net_profit <= 0 || executing === opp.id}
                                                className={`inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded-md text-white ${
                                                    opp.net_profit <= 0 || executing === opp.id
                                                        ? 'bg-gray-400 cursor-not-allowed'
                                                        : 'bg-blue-600 hover:bg-blue-700'
                                                }`}
                                            >
                                                {executing === opp.id ? 'Executing...' : 'Execute'}
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                    {opportunities.length === 0 && (
                        <div className="px-6 py-8 text-center text-gray-500">
                            No arbitrage opportunities found at the moment.
                        </div>
                    )}
                </div>

                {/* Profit Chart */}
                {opportunities.length > 0 && (
                    <div className="mt-8 bg-white rounded-lg shadow p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Profit Distribution</h3>
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={opportunities.slice(0, 10)}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="id" />
                                <YAxis />
                                <Tooltip 
                                    formatter={(value: number) => [formatPrice(value), 'Profit']}
                                    labelFormatter={(label) => `Opportunity: ${label.slice(0, 8)}...`}
                                />
                                <Legend />
                                <Line 
                                    type="monotone" 
                                    dataKey="net_profit" 
                                    stroke="#10B981" 
                                    strokeWidth={2}
                                    name="Net Profit"
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ArbitrageDashboard;