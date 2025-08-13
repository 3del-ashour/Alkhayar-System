<?php

namespace App\Http\Controllers;

use App\Models\Shipment;
use Illuminate\Http\Request;

class ShipmentController extends Controller
{
    public function index()
    {
        $shipments = Shipment::latest()->get();
        return view('shipments.index', compact('shipments'));
    }

    public function store(Request $request)
    {
        $data = $request->validate([
            'reference_number' => 'required|string|unique:shipments',
            'origin' => 'required|string',
            'destination' => 'required|string',
            'type' => 'nullable|string',
            'status' => 'required|string',
            'driver' => 'nullable|string',
            'notes' => 'nullable|string',
        ]);

        Shipment::create($data);
        return redirect()->route('shipments.index');
    }

    public function update(Request $request, Shipment $shipment)
    {
        $data = $request->validate([
            'origin' => 'required|string',
            'destination' => 'required|string',
            'type' => 'nullable|string',
            'status' => 'required|string',
            'driver' => 'nullable|string',
            'notes' => 'nullable|string',
        ]);

        $shipment->update($data);
        return redirect()->route('shipments.index');
    }

    public function destroy(Shipment $shipment)
    {
        $shipment->delete();
        return redirect()->route('shipments.index');
    }
}
