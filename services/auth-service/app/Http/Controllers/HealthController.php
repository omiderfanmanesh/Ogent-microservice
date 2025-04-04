<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class HealthController extends Controller
{
    /**
     * Health check endpoint
     *
     * @return \Illuminate\Http\JsonResponse
     */
    public function index()
    {
        return response()->json([
            'status' => 'ok',
            'timestamp' => now()->toDateTimeString(),
        ]);
    }
} 